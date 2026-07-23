/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/* Boots a libkrun micro-VM and never returns: krun_start_enter() turns this
 * process into the VMM, with the guest console wired to our stdin/stdout.
 * libkrun.dylib is dlopen'd so this binary has no link-time dependency on it,
 * and libkrunfw is preloaded by absolute path so libkrun's bare-name
 * dlopen("libkrunfw.5.dylib") resolves to the already-loaded image. */

#include <dlfcn.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

typedef int32_t (*krun_set_log_level_t)(uint32_t);
typedef int32_t (*krun_create_ctx_t)(void);
typedef int32_t (*krun_set_vm_config_t)(uint32_t, uint8_t, uint32_t);
typedef int32_t (*krun_set_root_t)(uint32_t, const char*);
typedef int32_t (*krun_set_workdir_t)(uint32_t, const char*);
typedef int32_t (*krun_set_exec_t)(uint32_t, const char*, const char* const[],
                                   const char* const[]);
typedef int32_t (*krun_start_enter_t)(uint32_t);

static void usage(const char* argv0) {
  fprintf(stderr,
          "usage: %s --lib <libkrun.dylib> --krunfw <libkrunfw.5.dylib> "
          "--root <rootfs-dir> [--mem <MiB>] [--cpus <n>] [--workdir <dir>] "
          "[--verbose] -- <exec-path> [args...]\n",
          argv0);
  exit(2);
}

int main(int argc, char** argv) {
  const char* lib_path = NULL;
  const char* krunfw_path = NULL;
  const char* root_path = NULL;
  const char* workdir = "/root";
  long mem_mib = 512;
  long cpus = 2;
  int verbose = 0;
  int guest_argv_start = -1;

  for (int i = 1; i < argc; i++) {
    if (!strcmp(argv[i], "--lib") && i + 1 < argc) {
      lib_path = argv[++i];
    } else if (!strcmp(argv[i], "--krunfw") && i + 1 < argc) {
      krunfw_path = argv[++i];
    } else if (!strcmp(argv[i], "--root") && i + 1 < argc) {
      root_path = argv[++i];
    } else if (!strcmp(argv[i], "--mem") && i + 1 < argc) {
      mem_mib = strtol(argv[++i], NULL, 10);
    } else if (!strcmp(argv[i], "--cpus") && i + 1 < argc) {
      cpus = strtol(argv[++i], NULL, 10);
    } else if (!strcmp(argv[i], "--workdir") && i + 1 < argc) {
      workdir = argv[++i];
    } else if (!strcmp(argv[i], "--verbose")) {
      verbose = 1;
    } else if (!strcmp(argv[i], "--")) {
      guest_argv_start = i + 1;
      break;
    } else {
      usage(argv[0]);
    }
  }

  if (!lib_path || !krunfw_path || !root_path || guest_argv_start < 0 ||
      guest_argv_start >= argc) {
    usage(argv[0]);
  }
  if (mem_mib <= 0 || cpus <= 0 || cpus > 255) {
    usage(argv[0]);
  }

  if (!dlopen(krunfw_path, RTLD_NOW | RTLD_GLOBAL)) {
    fprintf(stderr, "harness-vm-helper: failed to load %s: %s\n", krunfw_path,
            dlerror());
    return 1;
  }

  void* lib = dlopen(lib_path, RTLD_NOW);
  if (!lib) {
    fprintf(stderr, "harness-vm-helper: failed to load %s: %s\n", lib_path,
            dlerror());
    return 1;
  }

#define RESOLVE(name)                                                    \
  name##_t name = (name##_t)dlsym(lib, #name);                           \
  if (!name) {                                                           \
    fprintf(stderr, "harness-vm-helper: missing symbol %s: %s\n", #name, \
            dlerror());                                                  \
    return 1;                                                            \
  }
  RESOLVE(krun_set_log_level)
  RESOLVE(krun_create_ctx)
  RESOLVE(krun_set_vm_config)
  RESOLVE(krun_set_root)
  RESOLVE(krun_set_workdir)
  RESOLVE(krun_set_exec)
  RESOLVE(krun_start_enter)
#undef RESOLVE

  if (verbose) {
    krun_set_log_level(3);
  }

  int32_t ctx = krun_create_ctx();
  if (ctx < 0) {
    fprintf(stderr, "harness-vm-helper: krun_create_ctx failed: %d\n", ctx);
    return 1;
  }

#define CHECK(call)                                                      \
  do {                                                                   \
    int32_t err = (call);                                                \
    if (err < 0) {                                                       \
      fprintf(stderr, "harness-vm-helper: %s failed: %d\n", #call, err); \
      return 1;                                                          \
    }                                                                    \
  } while (0)

  CHECK(krun_set_vm_config((uint32_t)ctx, (uint8_t)cpus, (uint32_t)mem_mib));
  CHECK(krun_set_root((uint32_t)ctx, root_path));
  CHECK(krun_set_workdir((uint32_t)ctx, workdir));

  const char* exec_path = argv[guest_argv_start];
  /* argv[0] for the guest process is implicit (exec_path); pass the rest. */
  const char** guest_argv =
      calloc((size_t)(argc - guest_argv_start), sizeof(char*));
  if (!guest_argv) {
    return 1;
  }
  for (int i = guest_argv_start + 1; i < argc; i++) {
    guest_argv[i - guest_argv_start - 1] = argv[i];
  }
  static const char* const guest_envp[] = {
      "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
      "HOME=/root", "TERM=dumb", NULL};
  CHECK(krun_set_exec((uint32_t)ctx, exec_path, guest_argv, guest_envp));

  fprintf(stderr,
          "harness-vm-helper[%d]: entering microVM: root=%s mem=%ldMiB "
          "cpus=%ld exec=%s\n",
          getpid(), root_path, mem_mib, cpus, exec_path);
  fflush(stderr);

  /* Does not return on success; the process becomes the VMM and exits with
   * the guest workload's exit code. */
  int32_t err = krun_start_enter((uint32_t)ctx);
  fprintf(stderr, "harness-vm-helper: krun_start_enter failed: %d\n", err);
  return 1;
}
