/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/* Boots a libkrun micro-VM and never returns: krun_start_enter() turns this
 * process into the VMM, with the guest console wired to our stdin/stdout.
 * libkrun.dylib is dlopen'd so this binary has no link-time dependency on it,
 * and libkrunfw is preloaded by absolute path so libkrun's bare-name
 * dlopen("libkrunfw.5.dylib") resolves to the already-loaded image. */

#include <dirent.h>
#include <dlfcn.h>
#include <errno.h>
#include <libgen.h>
#include <limits.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

/* From libsandbox (same private API Firefox uses in
 * security/sandbox/mac/Sandbox.mm). */
extern int sandbox_init_with_parameters(const char* profile, uint64_t flags,
                                        const char* const parameters[],
                                        char** errorbuf);
extern void sandbox_free_error(char* errorbuf);

typedef int32_t (*krun_set_log_level_t)(uint32_t);
typedef int32_t (*krun_create_ctx_t)(void);
typedef int32_t (*krun_set_vm_config_t)(uint32_t, uint8_t, uint32_t);
typedef int32_t (*krun_set_root_t)(uint32_t, const char*);
typedef int32_t (*krun_set_workdir_t)(uint32_t, const char*);
typedef int32_t (*krun_set_exec_t)(uint32_t, const char*, const char* const[],
                                   const char* const[]);
typedef int32_t (*krun_start_enter_t)(uint32_t);
typedef int32_t (*krun_add_virtiofs3_t)(uint32_t, const char*, const char*,
                                        uint64_t, bool);
typedef int32_t (*krun_add_vsock_port_t)(uint32_t, uint32_t, const char*);
typedef int32_t (*krun_add_vsock_port2_t)(uint32_t, uint32_t, const char*,
                                          bool);
typedef int32_t (*krun_disable_implicit_vsock_t)(uint32_t);
typedef int32_t (*krun_add_vsock_t)(uint32_t, uint32_t);

#define MAX_VOLUMES 8

static void usage(const char* argv0) {
  fprintf(stderr,
          "usage: %s --lib <libkrun.dylib> --krunfw <libkrunfw.5.dylib> "
          "--root <rootfs-dir> [--mem <MiB>] [--cpus <n>] [--workdir <dir>] "
          "[--vsock <port>:<unix-socket-path>] [--volume <host-dir>:<tag>] "
          "[--allow-net] [--no-seatbelt] [--verbose] -- <exec-path> "
          "[args...]\n",
          argv0);
  exit(2);
}

/* ---- Seatbelt jailer ----
 * A guest-triggerable bug in libkrun's device emulation (virtio-fs above
 * all) would otherwise run with the user's full privileges. Confine this
 * process to the paths it legitimately needs before any guest-controlled
 * data is parsed. */

static char profile_buf[16384];
static size_t profile_len;

static void profile_add(const char* text) {
  size_t len = strlen(text);
  if (profile_len + len >= sizeof(profile_buf)) {
    fprintf(stderr, "harness-vm-helper: sandbox profile too large\n");
    exit(1);
  }
  memcpy(profile_buf + profile_len, text, len);
  profile_len += len;
  profile_buf[profile_len] = 0;
}

static void profile_add_path(const char* kind, const char* path) {
  if (strchr(path, '"')) {
    fprintf(stderr, "harness-vm-helper: unsupported character in path: %s\n",
            path);
    exit(1);
  }
  profile_add("(");
  profile_add(kind);
  profile_add(" \"");
  profile_add(path);
  profile_add("\")");
}

static void resolved_dir_of(const char* file_path, char* out, size_t out_len) {
  char resolved[PATH_MAX];
  if (!realpath(file_path, resolved)) {
    fprintf(stderr, "harness-vm-helper: cannot resolve %s\n", file_path);
    exit(1);
  }
  char* dir = dirname(resolved);
  snprintf(out, out_len, "%s", dir);
}

/* Canonicalizes the parent directory of a path that may not exist yet. */
static void canonical_parent(const char* path, char* out, size_t out_len) {
  char copy[PATH_MAX];
  snprintf(copy, sizeof(copy), "%s", path);
  char resolved[PATH_MAX];
  if (!realpath(dirname(copy), resolved)) {
    fprintf(stderr, "harness-vm-helper: cannot resolve parent of %s\n", path);
    exit(1);
  }
  snprintf(out, out_len, "%s", resolved);
}

static void seatbelt_allow_socket(const char* path) {
  char dir[PATH_MAX];
  canonical_parent(path, dir, sizeof(dir));
  char copy[PATH_MAX];
  snprintf(copy, sizeof(copy), "%s", path);
  char canonical[PATH_MAX];
  snprintf(canonical, sizeof(canonical), "%s/%s", dir, basename(copy));
  profile_add("(allow file-read* file-write* network-bind network-outbound ");
  profile_add_path("literal", canonical);
  profile_add(")\n");
}

static void apply_seatbelt(const char* lib_path, const char* krunfw_path,
                           const char* root_path, const char* vsock_path,
                           const char* vsock_out_path,
                           const char* const volume_paths[],
                           const int volume_ro[], int num_volumes) {
  char root_real[PATH_MAX];
  if (!realpath(root_path, root_real)) {
    fprintf(stderr, "harness-vm-helper: cannot resolve root %s\n", root_path);
    exit(1);
  }
  char lib_dir[PATH_MAX];
  char krunfw_dir[PATH_MAX];
  resolved_dir_of(lib_path, lib_dir, sizeof(lib_dir));
  resolved_dir_of(krunfw_path, krunfw_dir, sizeof(krunfw_dir));

  profile_add(
      "(version 1)\n"
      "(deny default)\n"
      "(allow signal (target self))\n"
      "(allow process-info* (target self))\n"
      "(allow sysctl-read)\n"
      "(allow file-read-metadata)\n"
      "(allow file-ioctl (literal \"/dev/null\"))\n"
      "(allow file-read* (literal \"/dev/urandom\") (literal \"/dev/random\")"
      " (literal \"/dev/null\") (literal \"/dev/zero\")"
      " (subpath \"/usr/lib\") (subpath \"/System\")"
      " (subpath \"/usr/share\"))\n"
      "(allow file-write-data (literal \"/dev/null\"))\n"
      "(allow file-map-executable"
      " (subpath \"/usr/lib\") (subpath \"/System\"))\n");

  profile_add("(allow file-read* file-map-executable ");
  profile_add_path("subpath", lib_dir);
  if (strcmp(lib_dir, krunfw_dir)) {
    profile_add_path("subpath", krunfw_dir);
  }
  profile_add(")\n");

  profile_add("(allow file-read* file-write* ");
  profile_add_path("subpath", root_real);
  for (int i = 0; i < num_volumes; i++) {
    char vol_real[PATH_MAX];
    if (!realpath(volume_paths[i], vol_real)) {
      fprintf(stderr, "harness-vm-helper: cannot resolve volume %s\n",
              volume_paths[i]);
      exit(1);
    }
    if (!volume_ro[i]) {
      profile_add_path("subpath", vol_real);
    }
  }
  profile_add(")\n");

  /* Read-only volumes: this process cannot write them even if the guest
   * defeats the virtio-fs read_only flag. */
  profile_add("(allow file-read* ");
  profile_add_path("subpath", root_real); /* keep list non-empty */
  for (int i = 0; i < num_volumes; i++) {
    if (volume_ro[i]) {
      char vol_real[PATH_MAX];
      if (!realpath(volume_paths[i], vol_real)) {
        fprintf(stderr, "harness-vm-helper: cannot resolve volume %s\n",
                volume_paths[i]);
        exit(1);
      }
      profile_add_path("subpath", vol_real);
    }
  }
  profile_add(")\n");

  /* Seatbelt matches canonical paths (/tmp is a symlink to /private/tmp),
   * and socket files may not exist yet: canonicalize the directory and
   * re-append the basename. */
  if (vsock_path) {
    seatbelt_allow_socket(vsock_path);
  }
  if (vsock_out_path) {
    seatbelt_allow_socket(vsock_out_path);
  }

  char* errorbuf = NULL;
  if (sandbox_init_with_parameters(profile_buf, 0, NULL, &errorbuf)) {
    fprintf(stderr, "harness-vm-helper: sandbox_init failed: %s\n",
            errorbuf ? errorbuf : "unknown");
    sandbox_free_error(errorbuf);
    exit(1);
  }
  fprintf(stderr, "harness-vm-helper: seatbelt sandbox applied\n");
}

int main(int argc, char** argv) {
  const char* lib_path = NULL;
  const char* krunfw_path = NULL;
  const char* root_path = NULL;
  const char* workdir = "/root";
  long mem_mib = 512;
  long cpus = 2;
  int verbose = 0;
  int allow_net = 0;
  int no_seatbelt = 0;
  const char* seatbelt_selftest = NULL;
  long vsock_port = 0;
  const char* vsock_path = NULL;
  long vsock_out_port = 0;
  const char* vsock_out_path = NULL;
  const char* volume_paths[MAX_VOLUMES];
  const char* volume_tags[MAX_VOLUMES];
  int volume_ro[MAX_VOLUMES];
  int num_volumes = 0;
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
    } else if (!strcmp(argv[i], "--vsock") && i + 1 < argc) {
      char* spec = argv[++i];
      char* sep = strchr(spec, ':');
      if (!sep || sep == spec || !sep[1]) {
        usage(argv[0]);
      }
      vsock_port = strtol(spec, NULL, 10);
      vsock_path = sep + 1;
      if (vsock_port <= 0) {
        usage(argv[0]);
      }
    } else if (!strcmp(argv[i], "--vsock-out") && i + 1 < argc) {
      /* Guest-initiated: guest connects to this vsock port and libkrun
       * connects out to the host unix socket (the policy proxy). */
      char* spec = argv[++i];
      char* sep = strchr(spec, ':');
      if (!sep || sep == spec || !sep[1]) {
        usage(argv[0]);
      }
      vsock_out_port = strtol(spec, NULL, 10);
      vsock_out_path = sep + 1;
      if (vsock_out_port <= 0) {
        usage(argv[0]);
      }
    } else if (!strcmp(argv[i], "--volume") && i + 1 < argc) {
      char* spec = argv[++i];
      int read_only = 0;
      size_t spec_len = strlen(spec);
      if (spec_len > 3 && !strcmp(spec + spec_len - 3, ":ro")) {
        spec[spec_len - 3] = '\0';
        read_only = 1;
      }
      char* sep = strrchr(spec, ':');
      if (!sep || sep == spec || !sep[1] || num_volumes == MAX_VOLUMES) {
        usage(argv[0]);
      }
      *sep = '\0';
      volume_paths[num_volumes] = spec;
      volume_tags[num_volumes] = sep + 1;
      volume_ro[num_volumes] = read_only;
      num_volumes++;
    } else if (!strcmp(argv[i], "--allow-net")) {
      allow_net = 1;
    } else if (!strcmp(argv[i], "--no-seatbelt")) {
      no_seatbelt = 1;
    } else if (!strcmp(argv[i], "--seatbelt-selftest") && i + 1 < argc) {
      seatbelt_selftest = argv[++i];
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

  if (!no_seatbelt) {
    apply_seatbelt(lib_path, krunfw_path, root_path, vsock_path,
                   vsock_out_path, volume_paths, volume_ro, num_volumes);
  }

  if (seatbelt_selftest) {
    /* Prints whether a path is readable under the applied sandbox, so tests
     * can assert both the allow and the deny side. */
    FILE* f = fopen(seatbelt_selftest, "r");
    printf("selftest %s: %s\n", seatbelt_selftest, f ? "readable" : "denied");
    if (f) {
      fclose(f);
    }
    return 0;
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
  RESOLVE(krun_add_virtiofs3)
  RESOLVE(krun_add_vsock_port)
  RESOLVE(krun_add_vsock_port2)
  RESOLVE(krun_disable_implicit_vsock)
  RESOLVE(krun_add_vsock)
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

  for (int i = 0; i < num_volumes; i++) {
    /* Fail fast with a readable error instead of a virtio-fs worker panic
     * mid-boot. EPERM here usually means macOS TCC privacy protection
     * (Downloads/Desktop/Documents) denied this process. */
    DIR* probe = opendir(volume_paths[i]);
    if (!probe) {
      fprintf(stderr,
              "harness-vm-helper: cannot access volume %s: %s%s\n",
              volume_paths[i], strerror(errno),
              errno == EPERM || errno == EACCES
                  ? " (macOS privacy protection for this folder?)"
                  : "");
      return 1;
    }
    closedir(probe);
    /* read_only here is host-side enforcement inside libkrun; the seatbelt
     * profile independently withholds write access for these subpaths, and
     * the guest additionally mounts them -o ro. */
    CHECK(krun_add_virtiofs3((uint32_t)ctx, volume_tags[i], volume_paths[i], 0,
                             volume_ro[i] != 0));
  }

  /* The implicit vsock device enables TSI hijacking, which transparently
   * gives the guest outbound network access through the host. Replace it
   * with a plain vsock device (IPC only) unless networking was requested. */
  if (!allow_net) {
    CHECK(krun_disable_implicit_vsock((uint32_t)ctx));
    if (vsock_path) {
      CHECK(krun_add_vsock((uint32_t)ctx, 0));
    }
  }
  if (vsock_path) {
    unlink(vsock_path);
    CHECK(krun_add_vsock_port2((uint32_t)ctx, (uint32_t)vsock_port, vsock_path,
                               true));
  }
  if (vsock_out_path) {
    CHECK(krun_add_vsock_port((uint32_t)ctx, (uint32_t)vsock_out_port,
                              vsock_out_path));
  }

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
