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

#include <arpa/inet.h>
#include <linux/vm_sockets.h>
#include <netinet/in.h>
#include <pty.h>

#define JSMN_STATIC
#include "jsmn.h"

#define AGENT_PORT 1024
#define PROXY_VSOCK_PORT 1025
#define PROXY_TCP_PORT 3128
#define MAX_PROXY_CONNS 8
#define PROXY_BUF (64 * 1024)
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

static int tok_bool(const char* json, const jsmntok_t* tok) {
  return tok->type == JSMN_PRIMITIVE && json[tok->start] == 't';
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
  int stdin_hold; /* interactive: keep stdin open when drained */
  int is_tty;
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

static void job_child_setup(const char* cmd, const char* cwd,
                            char* const env_keys[], char* const env_vals[],
                            int env_count) {
  /* Route HTTP(S) through the host policy proxy by default; the request
   * env may override. Non-proxied protocols have no route at all. */
  setenv("http_proxy", "http://127.0.0.1:3128", 0);
  setenv("https_proxy", "http://127.0.0.1:3128", 0);
  setenv("HTTP_PROXY", "http://127.0.0.1:3128", 0);
  setenv("HTTPS_PROXY", "http://127.0.0.1:3128", 0);
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

static void spawn_job(FILE* reply, int64_t id, const char* cmd, const char* cwd,
                      int64_t timeout_ms, char* const env_keys[],
                      char* const env_vals[], int env_count, char* stdin_buf,
                      size_t stdin_len, int is_tty, int interactive) {
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

  if (is_tty) {
    /* PTY job: merged output and input both ride the master fd. */
    int master;
    pid_t pid = forkpty(&master, NULL, NULL, NULL);
    if (pid < 0) {
      fprintf(reply, "{\"id\":%lld,\"error\":\"forkpty failed\"}\n",
              (long long)id);
      free(stdin_buf);
      return;
    }
    if (pid == 0) {
      job_child_setup(cmd, cwd, env_keys, env_vals, env_count);
    }
    fcntl(master, F_SETFL, O_NONBLOCK);
    memset(job, 0, sizeof(*job));
    job->active = 1;
    job->id = id;
    job->pid = pid;
    job->is_tty = 1;
    job->fds[0] = master;
    job->fds[1] = -1;
    job->deadline = now_ms() + timeout_ms;
    job->stdin_hold = 1;
    if (stdin_len) {
      job->stdin_fd = dup(master);
      job->stdin_buf = stdin_buf;
      job->stdin_len = stdin_len;
    } else {
      job->stdin_fd = dup(master);
      free(stdin_buf);
    }
    fcntl(job->stdin_fd, F_SETFL, O_NONBLOCK);
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
    job_child_setup(cmd, cwd, env_keys, env_vals, env_count);
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
  job->stdin_hold = interactive;
  if (stdin_len || interactive) {
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

static struct job* find_job(int64_t target_id) {
  for (int i = 0; i < MAX_JOBS; i++) {
    if (jobs[i].active && jobs[i].id == target_id) {
      return &jobs[i];
    }
  }
  return NULL;
}

/* Appends data to a running job's stdin buffer (pumped by the poll loop). */
static void job_input(FILE* reply, int64_t id, int64_t target_id, char* data,
                      size_t data_len) {
  struct job* job = find_job(target_id);
  if (!job || job->stdin_fd < 0) {
    fprintf(reply, "{\"id\":%lld,\"error\":\"no writable stdin\"}\n",
            (long long)id);
    free(data);
    return;
  }
  size_t remaining = job->stdin_len - job->stdin_off;
  char* merged = malloc(remaining + data_len);
  if (!merged) {
    fprintf(reply, "{\"id\":%lld,\"error\":\"oom\"}\n", (long long)id);
    free(data);
    return;
  }
  memcpy(merged, job->stdin_buf + job->stdin_off, remaining);
  memcpy(merged + remaining, data, data_len);
  free(job->stdin_buf);
  free(data);
  job->stdin_buf = merged;
  job->stdin_len = remaining + data_len;
  job->stdin_off = 0;
  fprintf(reply, "{\"id\":%lld,\"ok\":true}\n", (long long)id);
  fflush(reply);
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

/* ---- egress proxy forwarder ----
 * Guest programs speak plain HTTP-proxy to 127.0.0.1:3128 (http_proxy env);
 * each accepted connection is spliced onto vsock port 1025, which libkrun
 * forwards to the policy proxy in the Firefox parent. The guest never has a
 * NIC; this is the only byte channel out besides the control socket. */

struct proxy_conn {
  int active;
  int tcp_fd;
  int vsock_fd;
  char to_vsock[PROXY_BUF];
  size_t tv_len, tv_off;
  char to_tcp[PROXY_BUF];
  size_t tt_len, tt_off;
};

static struct proxy_conn proxy_conns[MAX_PROXY_CONNS];

static int proxy_listen_fd = -1;

static void proxy_setup(void) {
  proxy_listen_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (proxy_listen_fd < 0) {
    return;
  }
  int one = 1;
  setsockopt(proxy_listen_fd, SOL_SOCKET, SO_REUSEADDR, &one, sizeof(one));
  struct sockaddr_in addr = {0};
  addr.sin_family = AF_INET;
  addr.sin_port = htons(PROXY_TCP_PORT);
  addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
  if (bind(proxy_listen_fd, (struct sockaddr*)&addr, sizeof(addr)) ||
      listen(proxy_listen_fd, 4)) {
    close(proxy_listen_fd);
    proxy_listen_fd = -1;
    return;
  }
  fprintf(stderr, "guest-agent: proxy forwarder on 127.0.0.1:%d\n",
          PROXY_TCP_PORT);
}

static void proxy_conn_close(struct proxy_conn* conn) {
  close(conn->tcp_fd);
  close(conn->vsock_fd);
  conn->active = 0;
}

static void proxy_accept(void) {
  int tcp_fd = accept(proxy_listen_fd, NULL, NULL);
  if (tcp_fd < 0) {
    return;
  }
  struct proxy_conn* conn = NULL;
  for (int i = 0; i < MAX_PROXY_CONNS; i++) {
    if (!proxy_conns[i].active) {
      conn = &proxy_conns[i];
      break;
    }
  }
  if (!conn) {
    close(tcp_fd);
    return;
  }
  int vsock_fd = socket(AF_VSOCK, SOCK_STREAM, 0);
  struct sockaddr_vm addr = {0};
  addr.svm_family = AF_VSOCK;
  addr.svm_port = PROXY_VSOCK_PORT;
  addr.svm_cid = VMADDR_CID_HOST;
  if (vsock_fd < 0 ||
      connect(vsock_fd, (struct sockaddr*)&addr, sizeof(addr))) {
    if (vsock_fd >= 0) {
      close(vsock_fd);
    }
    close(tcp_fd);
    return;
  }
  fcntl(tcp_fd, F_SETFL, O_NONBLOCK);
  fcntl(vsock_fd, F_SETFL, O_NONBLOCK);
  memset(conn, 0, sizeof(*conn));
  conn->active = 1;
  conn->tcp_fd = tcp_fd;
  conn->vsock_fd = vsock_fd;
}

/* One direction of the splice: read into buf when empty, write out when
 * pending. Returns 0 on EOF/error. */
static int proxy_pump(int from, int to, char* buf, size_t* len, size_t* off) {
  if (*len == 0) {
    ssize_t n = read(from, buf, PROXY_BUF);
    if (n == 0 || (n < 0 && errno != EAGAIN && errno != EINTR)) {
      return 0;
    }
    if (n > 0) {
      *len = (size_t)n;
      *off = 0;
    }
  }
  while (*off < *len) {
    ssize_t n = write(to, buf + *off, *len - *off);
    if (n > 0) {
      *off += (size_t)n;
    } else if (errno == EAGAIN) {
      break;
    } else if (errno != EINTR) {
      return 0;
    }
  }
  if (*off >= *len) {
    *len = 0;
    *off = 0;
  }
  return 1;
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
  int64_t target_id = 0;
  int64_t timeout_ms = DEFAULT_TIMEOUT_MS;
  int is_tty = 0;
  int interactive = 0;
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
    } else if (tok_eq(line, key, "targetId")) {
      target_id = tok_int(line, &tokens[vi], 0);
    } else if (tok_eq(line, key, "op")) {
      op = tok_strdup(line, &tokens[vi]);
    } else if (tok_eq(line, key, "cmd")) {
      cmd = tok_strdup(line, &tokens[vi]);
    } else if (tok_eq(line, key, "cwd")) {
      cwd = tok_strdup(line, &tokens[vi]);
    } else if (tok_eq(line, key, "timeoutMs")) {
      timeout_ms = tok_int(line, &tokens[vi], DEFAULT_TIMEOUT_MS);
    } else if (tok_eq(line, key, "tty")) {
      is_tty = tok_bool(line, &tokens[vi]);
    } else if (tok_eq(line, key, "interactive")) {
      interactive = tok_bool(line, &tokens[vi]);
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
  } else if (op && !strcmp(op, "input")) {
    if (!stdin_buf) {
      stdin_buf = malloc(1);
      stdin_len = 0;
    }
    job_input(reply, id, target_id, stdin_buf, stdin_len);
  } else if (op && !strcmp(op, "inputEof")) {
    struct job* target = find_job(target_id);
    if (target && target->stdin_fd >= 0 && !target->is_tty) {
      target->stdin_hold = 0;
      if (target->stdin_off >= target->stdin_len) {
        close_job_stdin(target);
      }
    } else if (target && target->is_tty && target->stdin_fd >= 0) {
      /* Canonical-mode EOF for PTYs. */
      write(target->stdin_fd, "\x04", 1);
    }
    fprintf(reply, "{\"id\":%lld,\"ok\":true}\n", (long long)id);
    fflush(reply);
    free(stdin_buf);
  } else if (op && !strcmp(op, "kill")) {
    /* Kill the exec job whose request id is targetId; its normal done
     * message (exitCode 137) still follows via the poll loop. */
    int found = 0;
    for (int j = 0; j < MAX_JOBS; j++) {
      if (jobs[j].active && jobs[j].id == target_id) {
        kill(-jobs[j].pid, SIGKILL);
        found = 1;
      }
    }
    fprintf(reply, "{\"id\":%lld,\"ok\":true,\"found\":%s}\n", (long long)id,
            found ? "true" : "false");
    fflush(reply);
    free(stdin_buf);
  } else if (op && !strcmp(op, "exec") && cmd) {
    /* spawn_job takes ownership of stdin_buf */
    spawn_job(reply, id, cmd, cwd, timeout_ms, env_keys, env_vals, env_count,
              stdin_buf, stdin_len, is_tty, interactive);
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
    struct pollfd fds[2 + 3 * MAX_JOBS + 2 * MAX_PROXY_CONNS];
    struct job* fd_jobs[2 + 3 * MAX_JOBS + 2 * MAX_PROXY_CONNS];
    int fd_streams[2 + 3 * MAX_JOBS + 2 * MAX_PROXY_CONNS];
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
      if (jobs[i].stdin_fd >= 0 && jobs[i].stdin_off < jobs[i].stdin_len) {
        fds[nfds].fd = jobs[i].stdin_fd;
        fds[nfds].events = POLLOUT;
        fd_jobs[nfds] = &jobs[i];
        fd_streams[nfds] = 2; /* stdin marker */
        nfds++;
      }
    }

    int proxy_listen_idx = -1;
    if (proxy_listen_fd >= 0) {
      fds[nfds].fd = proxy_listen_fd;
      fds[nfds].events = POLLIN;
      fd_jobs[nfds] = NULL;
      proxy_listen_idx = (int)nfds;
      nfds++;
    }
    for (int i = 0; i < MAX_PROXY_CONNS; i++) {
      struct proxy_conn* pc = &proxy_conns[i];
      if (!pc->active) {
        continue;
      }
      fds[nfds].fd = pc->tcp_fd;
      fds[nfds].events = (pc->tv_len == 0 ? POLLIN : 0) |
                         (pc->tt_len > pc->tt_off ? POLLOUT : 0);
      fd_jobs[nfds] = NULL;
      nfds++;
      fds[nfds].fd = pc->vsock_fd;
      fds[nfds].events = (pc->tt_len == 0 ? POLLIN : 0) |
                         (pc->tv_len > pc->tv_off ? POLLOUT : 0);
      fd_jobs[nfds] = NULL;
      nfds++;
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
      if (!job) {
        continue; /* proxy fds are pumped below */
      }
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
        if (n < 0 && errno != EAGAIN && errno != EINTR) {
          close_job_stdin(job);
        } else if (job->stdin_off >= job->stdin_len && !job->stdin_hold) {
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

    if (proxy_listen_idx >= 0 && (fds[proxy_listen_idx].revents & POLLIN)) {
      proxy_accept();
    }
    for (int i = 0; i < MAX_PROXY_CONNS; i++) {
      struct proxy_conn* pc = &proxy_conns[i];
      if (!pc->active) {
        continue;
      }
      if (!proxy_pump(pc->tcp_fd, pc->vsock_fd, pc->to_vsock, &pc->tv_len,
                      &pc->tv_off) ||
          !proxy_pump(pc->vsock_fd, pc->tcp_fd, pc->to_tcp, &pc->tt_len,
                      &pc->tt_off)) {
        proxy_conn_close(pc);
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
  proxy_setup();

  for (;;) {
    int conn = accept(sock, NULL, NULL);
    if (conn < 0) {
      continue;
    }
    serve_connection(conn);
  }
}
