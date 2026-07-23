/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/* Runs inside the micro-VM guest. Listens on a vsock port and services
 * JSON-lines requests from the Firefox control plane:
 *   {"id":1,"op":"ping"}
 *   {"id":2,"op":"exec","cmd":"ls -la","cwd":"/workspace","timeoutMs":30000}
 * Responses:
 *   {"id":1,"ok":true}
 *   {"id":2,"exitCode":0,"stdout":"...","stderr":"...","truncated":false,
 *    "timedOut":false}
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
#define MAX_TOKENS 64
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
        case 'n': *w++ = '\n'; break;
        case 't': *w++ = '\t'; break;
        case 'r': *w++ = '\r'; break;
        case 'b': *w++ = '\b'; break;
        case 'f': *w++ = '\f'; break;
        case 'u':
          if (p + 4 < end) {
            char hex[5] = {p[1], p[2], p[3], p[4], 0};
            long code = strtol(hex, NULL, 16);
            *w++ = (code > 0 && code < 128) ? (char)code : '?';
            p += 4;
          }
          break;
        default: *w++ = *p; break;
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

static void json_escape_to(FILE* f, const char* s, size_t len) {
  for (size_t i = 0; i < len; i++) {
    unsigned char c = (unsigned char)s[i];
    switch (c) {
      case '"': fputs("\\\"", f); break;
      case '\\': fputs("\\\\", f); break;
      case '\n': fputs("\\n", f); break;
      case '\r': fputs("\\r", f); break;
      case '\t': fputs("\\t", f); break;
      default:
        if (c < 0x20 || c == 0x7f) {
          fprintf(f, "\\u%04x", c);
        } else {
          fputc(c, f);
        }
    }
  }
}

/* ---- exec ---- */

struct outbuf {
  char* data;
  size_t len;
  int truncated;
};

static void outbuf_append(struct outbuf* b, const char* data, size_t len) {
  if (b->len >= MAX_OUTPUT) {
    b->truncated = 1;
    return;
  }
  if (b->len + len > MAX_OUTPUT) {
    len = MAX_OUTPUT - b->len;
    b->truncated = 1;
  }
  memcpy(b->data + b->len, data, len);
  b->len += len;
}

static void handle_exec(FILE* reply, int64_t id, const char* cmd,
                        const char* cwd, int64_t timeout_ms) {
  int out_pipe[2];
  int err_pipe[2];
  if (pipe(out_pipe) || pipe(err_pipe)) {
    fprintf(reply, "{\"id\":%lld,\"error\":\"pipe failed\"}\n", (long long)id);
    return;
  }

  pid_t pid = fork();
  if (pid < 0) {
    fprintf(reply, "{\"id\":%lld,\"error\":\"fork failed\"}\n", (long long)id);
    return;
  }
  if (pid == 0) {
    setsid();
    dup2(out_pipe[1], 1);
    dup2(err_pipe[1], 2);
    close(out_pipe[0]);
    close(out_pipe[1]);
    close(err_pipe[0]);
    close(err_pipe[1]);
    if (cwd && chdir(cwd)) {
      fprintf(stderr, "guest-agent: chdir(%s): %s\n", cwd, strerror(errno));
      _exit(126);
    }
    execl("/bin/sh", "sh", "-c", cmd, (char*)NULL);
    _exit(127);
  }

  close(out_pipe[1]);
  close(err_pipe[1]);

  struct outbuf out = {malloc(MAX_OUTPUT), 0, 0};
  struct outbuf err = {malloc(MAX_OUTPUT), 0, 0};
  int64_t deadline = now_ms() + timeout_ms;
  int timed_out = 0;

  struct pollfd fds[2] = {{out_pipe[0], POLLIN, 0}, {err_pipe[0], POLLIN, 0}};
  int open_fds = 2;
  char buf[65536];
  while (open_fds > 0) {
    int wait = (int)(deadline - now_ms());
    if (wait <= 0) {
      timed_out = 1;
      kill(-pid, SIGKILL);
      break;
    }
    if (poll(fds, 2, wait) <= 0) {
      continue;
    }
    for (int i = 0; i < 2; i++) {
      if (!(fds[i].revents & (POLLIN | POLLHUP)) || fds[i].fd < 0) {
        continue;
      }
      ssize_t n = read(fds[i].fd, buf, sizeof(buf));
      if (n > 0) {
        outbuf_append(i == 0 ? &out : &err, buf, (size_t)n);
      } else {
        close(fds[i].fd);
        fds[i].fd = -1;
        open_fds--;
      }
    }
  }
  if (fds[0].fd >= 0) {
    close(fds[0].fd);
  }
  if (fds[1].fd >= 0) {
    close(fds[1].fd);
  }

  int status = 0;
  waitpid(pid, &status, 0);
  int exit_code = WIFEXITED(status)  ? WEXITSTATUS(status)
                  : WIFSIGNALED(status) ? 128 + WTERMSIG(status)
                                        : -1;

  fprintf(reply, "{\"id\":%lld,\"exitCode\":%d,\"stdout\":\"", (long long)id,
          exit_code);
  json_escape_to(reply, out.data, out.len);
  fputs("\",\"stderr\":\"", reply);
  json_escape_to(reply, err.data, err.len);
  fprintf(reply, "\",\"truncated\":%s,\"timedOut\":%s}\n",
          out.truncated || err.truncated ? "true" : "false",
          timed_out ? "true" : "false");
  free(out.data);
  free(err.data);
}

static void handle_line(FILE* reply, char* line) {
  jsmn_parser parser;
  jsmntok_t tokens[MAX_TOKENS];
  jsmn_init(&parser);
  int n = jsmn_parse(&parser, line, strlen(line), tokens, MAX_TOKENS);
  if (n < 1 || tokens[0].type != JSMN_OBJECT) {
    fputs("{\"id\":0,\"error\":\"bad request\"}\n", reply);
    return;
  }

  int64_t id = 0;
  int64_t timeout_ms = DEFAULT_TIMEOUT_MS;
  char* op = NULL;
  char* cmd = NULL;
  char* cwd = NULL;
  for (int i = 1; i < n - 1; i++) {
    if (tok_eq(line, &tokens[i], "id")) {
      id = tok_int(line, &tokens[i + 1], 0);
    } else if (tok_eq(line, &tokens[i], "op")) {
      op = tok_strdup(line, &tokens[i + 1]);
    } else if (tok_eq(line, &tokens[i], "cmd")) {
      cmd = tok_strdup(line, &tokens[i + 1]);
    } else if (tok_eq(line, &tokens[i], "cwd")) {
      cwd = tok_strdup(line, &tokens[i + 1]);
    } else if (tok_eq(line, &tokens[i], "timeoutMs")) {
      timeout_ms = tok_int(line, &tokens[i + 1], DEFAULT_TIMEOUT_MS);
    } else {
      continue;
    }
    i++; /* skip the value token */
  }
  if (timeout_ms <= 0 || timeout_ms > MAX_TIMEOUT_MS) {
    timeout_ms = DEFAULT_TIMEOUT_MS;
  }

  if (op && !strcmp(op, "ping")) {
    fprintf(reply, "{\"id\":%lld,\"ok\":true}\n", (long long)id);
  } else if (op && !strcmp(op, "exec") && cmd) {
    handle_exec(reply, id, cmd, cwd, timeout_ms);
  } else {
    fprintf(reply, "{\"id\":%lld,\"error\":\"unknown op\"}\n", (long long)id);
  }
  free(op);
  free(cmd);
  free(cwd);
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
  if (bind(sock, (struct sockaddr*)&addr, sizeof(addr)) ||
      listen(sock, 1)) {
    perror("guest-agent: bind/listen");
    return 1;
  }
  fprintf(stderr, "guest-agent: listening on vsock port %d\n", AGENT_PORT);

  for (;;) {
    int conn = accept(sock, NULL, NULL);
    if (conn < 0) {
      continue;
    }
    FILE* in = fdopen(conn, "r");
    FILE* reply = fdopen(dup(conn), "w");
    if (!in || !reply) {
      close(conn);
      continue;
    }
    setvbuf(reply, NULL, _IOLBF, 0);
    char* line = malloc(MAX_REQUEST);
    while (line && fgets(line, MAX_REQUEST, in)) {
      handle_line(reply, line);
      fflush(reply);
    }
    free(line);
    fclose(in);
    fclose(reply);
  }
}
