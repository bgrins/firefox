/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this
 * file, You can obtain one at http://mozilla.org/MPL/2.0/. */

/* Runs a program inside the iOS Simulator from the directory named by the
 * IOS_SIM_CWD environment variable. `simctl spawn` doesn't keep the working
 * directory of its caller, and the Simulator has no shell to change it. */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(int argc, char** argv) {
  if (argc < 2) {
    fprintf(stderr, "usage: %s program [args...]\n", argv[0]);
    return 2;
  }
  const char* cwd = getenv("IOS_SIM_CWD");
  if (cwd && chdir(cwd) != 0) {
    perror("chdir");
    return 2;
  }
  execv(argv[1], argv + 1);
  perror("execv");
  return 2;
}
