/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/* Runs inside the micro-VM guest. Listens on a vsock port and services
 * JSON-lines requests from the Firefox control plane. Multiple exec jobs run
 * concurrently; their output is streamed as it arrives:
 *   -> {"id":1,"op":"ping"}
 *   <- {"id":1,"ok":true}
 *   -> {"id":2,"op":"exec","cmd":"ls -la","cwd":"/workspace","timeoutMs":30000}
 *   <- {"id":2,"stream":"stdout","data":"..."}   (0 or more, interleaved)
 *   <- {"id":2,"stream":"stderr","data":"..."}
 *   <- {"id":2,"done":true,"exitCode":0,"truncated":false,"timedOut":false}
 * Cross-compiled statically for aarch64-linux by setup-deps.sh (not mach);
 * HarnessVM copies the binary into the rootfs before each VM start. */

#include <errno.h>
#include <fcntl.h>
#include <poll.h>
#include <signal.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

#include <linux/vm_sockets.h>

#define JSMN_STATIC
#include "jsmn.h"

#define AGENT_PORT 1024
#define MAX_REQUEST (1024 * 1024)
#define MAX_OUTPUT (1024 * 1024)
#define MAX_TOKENS 256
#define MAX_ENV 64
#define MAX_JOBS 16
#define DEFAULT_TIMEOUT_MS 30000
#define MAX_TIMEOUT_MS (10 * 60 * 1000)

static int64_t now_ms(void) {
  struct timeval tv;
  gettimeofday(&tv, NULL);
  return (int64_t)tv.tv_sec * 1000 + tv.tv_usec / 1000;
}

/* ---- JSON helpers ---- */

static int tok_eq(const char* json, const jsmntok_t* tok, const char* s) {
  size_t len = (size_t)(tok->end - tok->start);
  return tok->type == JSMN_STRING && strlen(s) == len &&
         !strncmp(json + tok->start, s, len);
}

/* Unescape a JSON string token into a fresh buffer. Handles the escapes
 * JSON.stringify produces; \uXXXX outside ASCII becomes '?'. */
static char* tok_strdup(const char* json, const jsmntok_t* tok) {
  size_t len = (size_t)(tok->end - tok->start);
  char* out = malloc(len + 1);
  if (!out) {
    return NULL;
  }
  const char* p = json + tok->start;
  const char* end = json + tok->end;
  char* w = out;
  while (p < end) {
    if (*p == '\\' && p + 1 < end) {
      p++;
      switch (*p) {
        case 'n':
          *w++ = '\n';
          break;
        case 't':
          *w++ = '\t';
          break;
        case 'r':
          *w++ = '\r';
          break;
        case 'b':
          *w++ = '\b';
          break;
        case 'f':
          *w++ = '\f';
          break;
        case 'u':
          if (p + 4 < end) {
            char hex[5] = {p[1], p[2], p[3], p[4], 0};
            long code = strtol(hex, NULL, 16);
            *w++ = (code > 0 && code < 128) ? (char)code : '?';
            p += 4;
          }
          break;
        default:
          *w++ = *p;
          break;
      }
      p++;
    } else {
      *w++ = *p++;
    }
  }
  *w = 0;
  return out;
}

static int64_t tok_int(const char* json, const jsmntok_t* tok, int64_t dflt) {
  if (tok->type != JSMN_PRIMITIVE) {
    return dflt;
  }
  return strtoll(json + tok->start, NULL, 10);
}

/* Returns the index just past the subtree rooted at token i. */
static int tok_skip(const jsmntok_t* tokens, int i) {
  if (tokens[i].type == JSMN_OBJECT) {
    int pairs = tokens[i].size;
    i++;
    for (int k = 0; k < pairs; k++) {
      i++; /* key */
      i = tok_skip(tokens, i);
    }
    return i;
  }
  if (tokens[i].type == JSMN_ARRAY) {
    int items = tokens[i].size;
    i++;
    for (int k = 0; k < items; k++) {
      i = tok_skip(tokens, i);
    }
    return i;
  }
  return i + 1;
}

static int b64_value(char c) {
  if (c >= 'A' && c <= 'Z') {
    return c - 'A';
  }
  if (c >= 'a' && c <= 'z') {
    return c - 'a' + 26;
  }
  if (c >= '0' && c <= '9') {
    return c - '0' + 52;
  }
  if (c == '+') {
    return 62;
  }
  if (c == '/') {
    return 63;
  }
  return -1;
}

static char* b64_decode(const char* in, size_t* out_len) {
  size_t len = strlen(in);
  char* out = malloc(len ? (len / 4 + 1) * 3 : 1);
  if (!out) {
    return NULL;
  }
  size_t n = 0;
  int acc = 0;
  int bits = 0;
  for (size_t i = 0; i < len; i++) {
    int v = b64_value(in[i]);
    if (v < 0) {
      continue; /* padding or whitespace */
    }
    acc = (acc << 6) | v;
    bits += 6;
    if (bits >= 8) {
      bits -= 8;
      out[n++] = (char)((acc >> bits) & 0xff);
    }
  }
  *out_len = n;
  return out;
}

static void json_escape_to(FILE* f, const char* s, size_t len) {
  for (size_t i = 0; i < len; i++) {
    unsigned char c = (unsigned char)s[i];
    switch (c) {
      case '"':
        fputs("\\\"", f);
        break;
      case '\\':
        fputs("\\\\", f);
        break;
      case '\n':
        fputs("\\n", f);
        break;
      case '\r':
        fputs("\\r", f);
        break;
      case '\t':
        fputs("\\t", f);
        break;
      default:
        if (c < 0x20 || c == 0x7f) {
          fprintf(f, "\\u%04x", c);
        } else {
          fputc(c, f);
        }
    }
  }
}

/* ---- jobs ---- */

struct job {
  int active;
  int64_t id;
  pid_t pid;
  int fds[2]; /* stdout, stderr; -1 once closed */
  size_t sent[2];
  int stdin_fd; /* write end; -1 once closed */
  char* stdin_buf;
  size_t stdin_len;
  size_t stdin_off;
  int truncated;
  int timed_out;
  int64_t deadline;
};

static struct job jobs[MAX_JOBS];
static const char* const STREAM_NAMES[2] = {"stdout", "stderr"};

static void send_chunk(FILE* reply, struct job* job, int which,
                       const char* data, size_t len) {
  if (job->sent[which] >= MAX_OUTPUT) {
    job->truncated = 1;
    return;
  }
  if (job->sent[which] + len > MAX_OUTPUT) {
    len = MAX_OUTPUT - job->sent[which];
    job->truncated = 1;
  }
  job->sent[which] += len;
  fprintf(reply, "{\"id\":%lld,\"stream\":\"%s\",\"data\":\"",
          (long long)job->id, STREAM_NAMES[which]);
  json_escape_to(reply, data, len);
  fputs("\"}\n", reply);
  fflush(reply);
}

static void close_job_stdin(struct job* job) {
  if (job->stdin_fd >= 0) {
    close(job->stdin_fd);
    job->stdin_fd = -1;
  }
  free(job->stdin_buf);
  job->stdin_buf = NULL;
}

static void finish_job(FILE* reply, struct job* job) {
  close_job_stdin(job);
  int status = 0;
  waitpid(job->pid, &status, 0);
  int exit_code = WIFEXITED(status)     ? WEXITSTATUS(status)
                  : WIFSIGNALED(status) ? 128 + WTERMSIG(status)
                                        : -1;
  fprintf(reply,
          "{\"id\":%lld,\"done\":true,\"exitCode\":%d,\"truncated\":%s,"
          "\"timedOut\":%s}\n",
          (long long)job->id, exit_code, job->truncated ? "true" : "false",
          job->timed_out ? "true" : "false");
  fflush(reply);
  job->active = 0;
}

static void spawn_job(FILE* reply, int64_t id, const char* cmd,
                      const char* cwd, int64_t timeout_ms,
                      char* const env_keys[], char* const env_vals[],
                      int env_count, char* stdin_buf, size_t stdin_len) {
  struct job* job = NULL;
  for (int i = 0; i < MAX_JOBS; i++) {
    if (!jobs[i].active) {
      job = &jobs[i];
      break;
    }
  }
  if (!job) {
    fprintf(reply, "{\"id\":%lld,\"error\":\"too many concurrent jobs\"}\n",
            (long long)id);
    free(stdin_buf);
    return;
  }

  int in_pipe[2];
  int out_pipe[2];
  int err_pipe[2];
  if (pipe(in_pipe) || pipe(out_pipe) || pipe(err_pipe)) {
    fprintf(reply, "{\"id\":%lld,\"error\":\"pipe failed\"}\n", (long long)id);
    free(stdin_buf);
    return;
  }

  pid_t pid = fork();
  if (pid < 0) {
    fprintf(reply, "{\"id\":%lld,\"error\":\"fork failed\"}\n", (long long)id);
    free(stdin_buf);
    return;
  }
  if (pid == 0) {
    setsid();
    dup2(in_pipe[0], 0);
    dup2(out_pipe[1], 1);
    dup2(err_pipe[1], 2);
    close(in_pipe[0]);
    close(in_pipe[1]);
    close(out_pipe[0]);
    close(out_pipe[1]);
    close(err_pipe[0]);
    close(err_pipe[1]);
    for (int i = 0; i < env_count; i++) {
      setenv(env_keys[i], env_vals[i], 1);
    }
    if (cwd && chdir(cwd)) {
      fprintf(stderr, "guest-agent: chdir(%s): %s\n", cwd, strerror(errno));
      _exit(126);
    }
    execl("/bin/sh", "sh", "-c", cmd, (char*)NULL);
    _exit(127);
  }

  close(in_pipe[0]);
  close(out_pipe[1]);
  close(err_pipe[1]);
  fcntl(out_pipe[0], F_SETFL, O_NONBLOCK);
  fcntl(err_pipe[0], F_SETFL, O_NONBLOCK);
  fcntl(in_pipe[1], F_SETFL, O_NONBLOCK);

  memset(job, 0, sizeof(*job));
  job->active = 1;
  job->id = id;
  job->pid = pid;
  job->fds[0] = out_pipe[0];
  job->fds[1] = err_pipe[0];
  job->deadline = now_ms() + timeout_ms;
  if (stdin_len) {
    job->stdin_fd = in_pipe[1];
    job->stdin_buf = stdin_buf;
    job->stdin_len = stdin_len;
  } else {
    /* No stdin payload: give the child immediate EOF so tools that read
     * stdin never hang against the console. */
    close(in_pipe[1]);
    job->stdin_fd = -1;
    free(stdin_buf);
  }
}

static void kill_all_jobs(void) {
  for (int i = 0; i < MAX_JOBS; i++) {
    if (!jobs[i].active) {
      continue;
    }
    kill(-jobs[i].pid, SIGKILL);
    waitpid(jobs[i].pid, NULL, 0);
    close_job_stdin(&jobs[i]);
    for (int s = 0; s < 2; s++) {
      if (jobs[i].fds[s] >= 0) {
        close(jobs[i].fds[s]);
      }
    }
    jobs[i].active = 0;
  }
}

/* ---- request handling ---- */

static void handle_line(FILE* reply, char* line) {
  jsmn_parser parser;
  jsmntok_t tokens[MAX_TOKENS];
  jsmn_init(&parser);
  int n = jsmn_parse(&parser, line, strlen(line), tokens, MAX_TOKENS);
  if (n < 1 || tokens[0].type != JSMN_OBJECT) {
    fputs("{\"id\":0,\"error\":\"bad request\"}\n", reply);
    fflush(reply);
    return;
  }

  int64_t id = 0;
  int64_t timeout_ms = DEFAULT_TIMEOUT_MS;
  char* op = NULL;
  char* cmd = NULL;
  char* cwd = NULL;
  char* env_keys[MAX_ENV];
  char* env_vals[MAX_ENV];
  int env_count = 0;
  char* stdin_buf = NULL;
  size_t stdin_len = 0;

  int i = 1;
  while (i < n) {
    const jsmntok_t* key = &tokens[i];
    int vi = i + 1;
    if (vi >= n) {
      break;
    }
    if (tok_eq(line, key, "id")) {
      id = tok_int(line, &tokens[vi], 0);
    } else if (tok_eq(line, key, "op")) {
      op = tok_strdup(line, &tokens[vi]);
    } else if (tok_eq(line, key, "cmd")) {
      cmd = tok_strdup(line, &tokens[vi]);
    } else if (tok_eq(line, key, "cwd")) {
      cwd = tok_strdup(line, &tokens[vi]);
    } else if (tok_eq(line, key, "timeoutMs")) {
      timeout_ms = tok_int(line, &tokens[vi], DEFAULT_TIMEOUT_MS);
    } else if (tok_eq(line, key, "stdinB64")) {
      char* b64 = tok_strdup(line, &tokens[vi]);
      if (b64) {
        stdin_buf = b64_decode(b64, &stdin_len);
        free(b64);
      }
    } else if (tok_eq(line, key, "env") && tokens[vi].type == JSMN_OBJECT) {
      int pairs = tokens[vi].size;
      int ei = vi + 1;
      for (int p = 0; p < pairs && env_count < MAX_ENV; p++) {
        env_keys[env_count] = tok_strdup(line, &tokens[ei]);
        env_vals[env_count] = tok_strdup(line, &tokens[ei + 1]);
        if (env_keys[env_count] && env_vals[env_count]) {
          env_count++;
        }
        ei = tok_skip(tokens, ei + 1);
      }
    }
    i = tok_skip(tokens, vi);
  }
  if (timeout_ms <= 0 || timeout_ms > MAX_TIMEOUT_MS) {
    timeout_ms = DEFAULT_TIMEOUT_MS;
  }

  if (op && !strcmp(op, "ping")) {
    fprintf(reply, "{\"id\":%lld,\"ok\":true}\n", (long long)id);
    fflush(reply);
    free(stdin_buf);
  } else if (op && !strcmp(op, "exec") && cmd) {
    /* spawn_job takes ownership of stdin_buf */
    spawn_job(reply, id, cmd, cwd, timeout_ms, env_keys, env_vals, env_count,
              stdin_buf, stdin_len);
  } else {
    fprintf(reply, "{\"id\":%lld,\"error\":\"unknown op\"}\n", (long long)id);
    fflush(reply);
    free(stdin_buf);
  }
  free(op);
  free(cmd);
  free(cwd);
  for (int e = 0; e < env_count; e++) {
    free(env_keys[e]);
    free(env_vals[e]);
  }
}

static void serve_connection(int conn) {
  FILE* reply = fdopen(dup(conn), "w");
  if (!reply) {
    close(conn);
    return;
  }
  char* inbuf = malloc(MAX_REQUEST);
  size_t inlen = 0;
  char buf[65536];

  for (;;) {
    struct pollfd fds[1 + 3 * MAX_JOBS];
    struct job* fd_jobs[1 + 3 * MAX_JOBS];
    int fd_streams[1 + 3 * MAX_JOBS];
    nfds_t nfds = 0;

    fds[nfds].fd = conn;
    fds[nfds].events = POLLIN;
    fd_jobs[nfds] = NULL;
    nfds++;

    int64_t next_deadline = -1;
    for (int i = 0; i < MAX_JOBS; i++) {
      if (!jobs[i].active) {
        continue;
      }
      if (next_deadline < 0 || jobs[i].deadline < next_deadline) {
        next_deadline = jobs[i].deadline;
      }
      for (int s = 0; s < 2; s++) {
        if (jobs[i].fds[s] >= 0) {
          fds[nfds].fd = jobs[i].fds[s];
          fds[nfds].events = POLLIN;
          fd_jobs[nfds] = &jobs[i];
          fd_streams[nfds] = s;
          nfds++;
        }
      }
      if (jobs[i].stdin_fd >= 0) {
        fds[nfds].fd = jobs[i].stdin_fd;
        fds[nfds].events = POLLOUT;
        fd_jobs[nfds] = &jobs[i];
        fd_streams[nfds] = 2; /* stdin marker */
        nfds++;
      }
    }

    int timeout = -1;
    if (next_deadline >= 0) {
      int64_t wait = next_deadline - now_ms();
      timeout = wait < 0 ? 0 : (int)wait;
    }
    int ready = poll(fds, nfds, timeout);
    if (ready < 0 && errno != EINTR) {
      break;
    }

    /* Enforce timeouts. */
    int64_t now = now_ms();
    for (int i = 0; i < MAX_JOBS; i++) {
      if (jobs[i].active && !jobs[i].timed_out && now >= jobs[i].deadline) {
        jobs[i].timed_out = 1;
        kill(-jobs[i].pid, SIGKILL);
      }
    }

    /* Pump job stdin and output. */
    for (nfds_t f = 1; f < nfds; f++) {
      struct job* job = fd_jobs[f];
      int s = fd_streams[f];
      if (s == 2) {
        if (!(fds[f].revents & (POLLOUT | POLLERR | POLLHUP))) {
          continue;
        }
        if (fds[f].revents & (POLLERR | POLLHUP)) {
          close_job_stdin(job); /* child closed stdin early */
          continue;
        }
        ssize_t n = write(job->stdin_fd, job->stdin_buf + job->stdin_off,
                          job->stdin_len - job->stdin_off);
        if (n > 0) {
          job->stdin_off += (size_t)n;
        }
        if (job->stdin_off >= job->stdin_len ||
            (n < 0 && errno != EAGAIN && errno != EINTR)) {
          close_job_stdin(job);
        }
        continue;
      }
      if (!(fds[f].revents & (POLLIN | POLLHUP))) {
        continue;
      }
      ssize_t n = read(fds[f].fd, buf, sizeof(buf));
      if (n > 0) {
        send_chunk(reply, job, s, buf, (size_t)n);
      } else if (n == 0 || (n < 0 && errno != EAGAIN && errno != EINTR)) {
        close(job->fds[s]);
        job->fds[s] = -1;
        if (job->fds[0] < 0 && job->fds[1] < 0) {
          finish_job(reply, job);
        }
      }
    }

    if (ferror(reply)) {
      break; /* reply channel is dead; bail and clean up jobs */
    }

    /* Pump requests. */
    if (fds[0].revents & (POLLIN | POLLHUP)) {
      ssize_t n = read(conn, buf, sizeof(buf));
      if (n <= 0) {
        break; /* control plane went away */
      }
      if (inlen + (size_t)n > MAX_REQUEST - 1) {
        inlen = 0; /* oversized request; drop buffered data */
        continue;
      }
      memcpy(inbuf + inlen, buf, (size_t)n);
      inlen += (size_t)n;
      inbuf[inlen] = 0;
      char* start = inbuf;
      char* newline;
      while ((newline = strchr(start, '\n'))) {
        *newline = 0;
        handle_line(reply, start);
        start = newline + 1;
      }
      inlen -= (size_t)(start - inbuf);
      memmove(inbuf, start, inlen);
    }
  }

  kill_all_jobs();
  free(inbuf);
  fclose(reply);
  close(conn);
}

int main(void) {
  signal(SIGPIPE, SIG_IGN);

  int sock = socket(AF_VSOCK, SOCK_STREAM, 0);
  if (sock < 0) {
    perror("guest-agent: socket");
    return 1;
  }
  struct sockaddr_vm addr = {0};
  addr.svm_family = AF_VSOCK;
  addr.svm_port = AGENT_PORT;
  addr.svm_cid = VMADDR_CID_ANY;
  if (bind(sock, (struct sockaddr*)&addr, sizeof(addr)) || listen(sock, 1)) {
    perror("guest-agent: bind/listen");
    return 1;
  }
  fprintf(stderr, "guest-agent: listening on vsock port %d\n", AGENT_PORT);

  for (;;) {
    int conn = accept(sock, NULL, NULL);
    if (conn < 0) {
      continue;
    }
    serve_connection(conn);
  }
}
