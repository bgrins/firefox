/* This Source Code Form is subject to the terms of the Mozilla Public
 * License, v. 2.0. If a copy of the MPL was not distributed with this file,
 * You can obtain one at http://mozilla.org/MPL/2.0/. */

import React, { useState, useEffect, useRef, useCallback } from "react";
import { useSelector } from "react-redux";
import { WIDGET_REGISTRY, resolveWidgetSize } from "../WidgetsRegistry.mjs";

const sokobanEntry = WIDGET_REGISTRY.find(w => w.id === "sokobanGame");

// --- Microban levels (XSB format) ---
// # = wall, @ = player, + = player on goal, $ = box, * = box on goal, . = goal
const MICROBAN_LEVELS = [
  { id: 1, board: "####  \n# .#  \n#  ###\n#*@  #\n#  $ #\n#  ###\n####  " },
  { id: 2, board: "######\n#    #\n# #@ #\n# $* #\n# .* #\n#    #\n######" },
  { id: 3, board: "  ####   \n###  ####\n#     $ #\n# #  #$ #\n# . .#@ #\n#########" },
  { id: 4, board: "########\n#      #\n# .**$@#\n#      #\n#####  #\n    ####" },
  { id: 5, board: " #######\n #     #\n # .$. #\n## $@$ #\n#  .$. #\n#      #\n########" },
  { id: 6, board: "###### #####\n#    ###   #\n# $$     #@#\n# $ #...   #\n#   ########\n#####       " },
  { id: 7, board: "#######\n#     #\n# .$. #\n# $.$ #\n# .$. #\n# $.$ #\n#  @  #\n#######" },
  { id: 8, board: "  ######\n  # ..@#\n  # $$ #\n  ## ###\n   # #  \n   # #  \n#### #  \n#    ## \n# #   # \n#   # # \n###   # \n  ##### " },
  { id: 9, board: "##### \n#.  ##\n#@$$ #\n##   #\n ##  #\n  ##.#\n   ###" },
  { id: 10, board: "      #####\n      #.  #\n      #.# #\n#######.# #\n# @ $ $ $ #\n# # # # ###\n#       #  \n#########  " },
  { id: 11, board: "  ###### \n  #    # \n  # ##@##\n### # $ #\n# ..# $ #\n#       #\n#  ######\n####     " },
  { id: 12, board: "#####    \n#   ##   \n# $  #   \n## $ ####\n ###@.  #\n  #  .# #\n  #     #\n  #######" },
  { id: 13, board: "####   \n#. ##  \n#.@ #  \n#. $#  \n##$ ###\n # $  #\n #    #\n #  ###\n ####  " },
  { id: 14, board: "#######\n#     #\n# # # #\n#. $*@#\n#   ###\n#####  " },
  { id: 15, board: "     ### \n######@##\n#    .* #\n#   #   #\n#####$# #\n    #   #\n    #####" },
  { id: 16, board: " ####     \n #  ####  \n #     ## \n## ##   # \n#. .# @$##\n#   # $$ #\n#  .#    #\n##########" },
  { id: 17, board: "##### \n# @ # \n#...# \n#$$$##\n#    #\n#    #\n######" },
  { id: 18, board: "#######\n#     #\n#. .  #\n# ## ##\n#  $ # \n###$ # \n  #@ # \n  #  # \n  #### " },
  { id: 19, board: "########\n#   .. #\n#  @$$ #\n##### ##\n   #  # \n   #  # \n   #  # \n   #### " },
  { id: 20, board: "#######  \n#     ###\n#  @$$..#\n#### ## #\n  #     #\n  #  ####\n  #  #   \n  ####   " },
  { id: 21, board: "####   \n#  ####\n# . . #\n# $$#@#\n##    #\n ######" },
  { id: 22, board: "#####  \n#   ###\n#. .  #\n#   # #\n## #  #\n #@$$ #\n #    #\n #  ###\n ####  " },
  { id: 23, board: "#######\n#  *  #\n#     #\n## # ##\n #$@.# \n #   # \n ##### " },
  { id: 24, board: "# #####\n  #   #\n###$$@#\n#   ###\n#     #\n# . . #\n#######" },
  { id: 25, board: " ####  \n #  ###\n # $$ #\n##... #\n#  @$ #\n#   ###\n#####  " },
  { id: 26, board: " #####\n # @ #\n #   #\n###$ #\n# ...#\n# $$ #\n###  #\n  ####" },
  { id: 27, board: "###### \n#   .# \n# ## ##\n#  $$@#\n# #   #\n#.  ###\n#####  " },
  { id: 28, board: "#####  \n#   #  \n# @ #  \n# $$###\n##. . #\n #    #\n ######" },
  { id: 29, board: "     ##### \n     #   ##\n     #    #\n ######   #\n##     #. #\n# $ $ @  ##\n# ######.# \n#        # \n########## " },
  { id: 30, board: "####  \n#  ###\n# $$ #\n#... #\n# @$ #\n#   ##\n##### " },
  { id: 31, board: "  #### \n ##  # \n##@$.##\n# $$  #\n# . . #\n###   #\n  #####" },
  { id: 32, board: " ####  \n##  ###\n#     #\n#.**$@#\n#   ###\n##  #  \n ####  " },
  { id: 33, board: "#######\n#. #  #\n#  $  #\n#. $#@#\n#  $  #\n#. #  #\n#######" },
  { id: 34, board: "  ####   \n###  ####\n#       #\n#@$***. #\n#       #\n#########" },
  { id: 35, board: "  #### \n ##  # \n #. $# \n #.$ # \n #.$ # \n #.$ # \n #. $##\n #   @#\n ##   #\n  #####" },
  { id: 36, board: "####           \n#  ############\n# $ $ $ $ $ @ #\n# .....       #\n###############" },
  { id: 37, board: "      ###\n##### #.#\n#   ###.#\n#   $ #.#\n# $  $  #\n#####@# #\n    #   #\n    #####" },
  { id: 38, board: "##########\n#        #\n# ##.### #\n# # $$ . #\n# . @$## #\n#####    #\n    ######" },
  { id: 39, board: "#####     \n#   ####  \n# # # .#  \n#    $ ###\n### #$.  #\n#   #@   #\n# # ######\n#   #     \n#####     " },
  { id: 40, board: " ##### \n #   # \n##   ##\n# $$$ #\n# .+. #\n#######" },
  { id: 41, board: "####### \n#     # \n#@$$$ ##\n#  #...#\n##    ##\n ###### " },
  { id: 42, board: "   ####\n   #  #\n   #@ #\n####$.#\n#   $.#\n# # $.#\n#    ##\n###### " },
  { id: 43, board: "     ####\n     # @#\n     #  #\n###### .#\n#   $  .#\n#  $$# .#\n#    ####\n###  #   \n  ####   " },
  { id: 44, board: "#####\n#@$.#\n#####" },
  { id: 45, board: "######\n#... #\n#  $ #\n# #$##\n#  $ #\n#  @ #\n######" },
  { id: 46, board: " ######\n##    #\n#  ## #\n# # $ #\n#  * .#\n## #@##\n #   # \n ##### " },
  { id: 47, board: "  #######  \n###     #  \n# $ $   #  \n# ### #####\n# @ . .   #\n#   ###   #\n##### #####" },
  { id: 48, board: "######  \n#  @ #  \n#  # ## \n# .#  ##\n# .$$$ #\n# .#   #\n####   #\n   #####" },
  { id: 49, board: "######  \n# @  #  \n# $# #  \n# $  #  \n# $ ##  \n### ####\n #  #  #\n #...  #\n #     #\n #######" },
  { id: 50, board: "  ####    \n###  #####\n#  $  @..#\n# $    # #\n### #### #\n  #      #\n  ########" },
];

const Direction = { Up: "up", Down: "down", Left: "left", Right: "right" };

// --- Game Engine (ported from mega_sokoban) ---
function parseBoard(boardString) {
  const lines = boardString.split("\n");
  let player = null;
  const boxes = [];
  const goals = [];
  const walls = [];
  const height = lines.length;
  const width = Math.max(...lines.map(l => l.length));

  for (let y = 0; y < lines.length; y++) {
    const line = lines[y];
    for (let x = 0; x < line.length; x++) {
      const ch = line[x];
      const pos = { x, y };
      switch (ch) {
        case "#":
          walls.push(pos);
          break;
        case "@":
          player = pos;
          break;
        case "+":
          player = pos;
          goals.push(pos);
          break;
        case "$":
          boxes.push(pos);
          break;
        case "*":
          boxes.push(pos);
          goals.push(pos);
          break;
        case ".":
          goals.push(pos);
          break;
      }
    }
  }
  return { player, boxes, goals, walls, width, height };
}

function cloneState(state) {
  return {
    player: { ...state.player },
    boxes: state.boxes.map(b => ({ ...b })),
    goals: state.goals.map(g => ({ ...g })),
    walls: state.walls.map(w => ({ ...w })),
    width: state.width,
    height: state.height,
    moves: state.moves,
    pushes: state.pushes,
  };
}

function createEngine(level) {
  const parsed = parseBoard(level.board);
  if (!parsed.player) {
    throw new Error("Level must have a player position");
  }
  const initial = {
    player: { ...parsed.player },
    boxes: parsed.boxes.map(b => ({ ...b })),
    goals: parsed.goals.map(g => ({ ...g })),
    walls: parsed.walls.map(w => ({ ...w })),
    width: parsed.width,
    height: parsed.height,
    moves: 0,
    pushes: 0,
  };
  return {
    state: cloneState(initial),
    initialState: cloneState(initial),
    history: [],
    redoStack: [],
  };
}

function getDelta(direction) {
  switch (direction) {
    case Direction.Up:
      return { x: 0, y: -1 };
    case Direction.Down:
      return { x: 0, y: 1 };
    case Direction.Left:
      return { x: -1, y: 0 };
    case Direction.Right:
      return { x: 1, y: 0 };
  }
  return { x: 0, y: 0 };
}

function isInBounds(pos, state) {
  return pos.x >= 0 && pos.x < state.width && pos.y >= 0 && pos.y < state.height;
}

function isWall(pos, state) {
  return state.walls.some(w => w.x === pos.x && w.y === pos.y);
}

function findBoxAt(pos, state) {
  return state.boxes.findIndex(b => b.x === pos.x && b.y === pos.y);
}

function checkWin(state) {
  return state.boxes.every(box =>
    state.goals.some(goal => goal.x === box.x && goal.y === box.y)
  );
}

function movePlayer(engine, direction) {
  const { state } = engine;
  const delta = getDelta(direction);
  const newPos = { x: state.player.x + delta.x, y: state.player.y + delta.y };

  if (!isInBounds(newPos, state) || isWall(newPos, state)) {
    return { valid: false, engine };
  }

  const boxIdx = findBoxAt(newPos, state);
  if (boxIdx !== -1) {
    const newBoxPos = { x: newPos.x + delta.x, y: newPos.y + delta.y };
    if (
      !isInBounds(newBoxPos, state) ||
      isWall(newBoxPos, state) ||
      findBoxAt(newBoxPos, state) !== -1
    ) {
      return { valid: false, engine };
    }
    const newState = cloneState(state);
    newState.player = newPos;
    newState.boxes[boxIdx] = newBoxPos;
    newState.moves++;
    newState.pushes++;
    return {
      valid: true,
      engine: {
        ...engine,
        state: newState,
        history: [...engine.history, cloneState(state)],
        redoStack: [],
      },
      isWin: checkWin(newState),
    };
  }

  const newState = cloneState(state);
  newState.player = newPos;
  newState.moves++;
  return {
    valid: true,
    engine: {
      ...engine,
      state: newState,
      history: [...engine.history, cloneState(state)],
      redoStack: [],
    },
    isWin: checkWin(newState),
  };
}

function undoMove(engine) {
  if (engine.history.length === 0) {
    return engine;
  }
  const prev = engine.history[engine.history.length - 1];
  return {
    ...engine,
    state: prev,
    history: engine.history.slice(0, -1),
    redoStack: [...engine.redoStack, cloneState(engine.state)],
  };
}

function redoMove(engine) {
  if (engine.redoStack.length === 0) {
    return engine;
  }
  const next = engine.redoStack[engine.redoStack.length - 1];
  return {
    ...engine,
    state: next,
    history: [...engine.history, cloneState(engine.state)],
    redoStack: engine.redoStack.slice(0, -1),
  };
}

function resetEngine(engine) {
  return {
    ...engine,
    state: cloneState(engine.initialState),
    history: [],
    redoStack: [],
  };
}

// --- SVG paths for Kit faces ---
// Inline SVG data URIs for kit-happy and kit-concerned
const KIT_HAPPY_SVG = `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="50" height="40" fill="none"><g clip-path="url(#a)"><path fill="url(#b)" d="M44.334 5.63c-.848.998-.927 1.831-.927 1.831s-.082-.787-1.008-1.831c-1.47-1.649-5.76-1.182-5.102 2.753.631 3.792 6.103 7.91 6.11 7.914 0 0 5.47-4.208 6.112-7.996.653-3.853-3.795-4.312-5.185-2.671Z"/><path fill="url(#c)" d="M29.51.16c2.876.864-1.469 17.615-1.469 17.615l-14.814-3.82s2.326-3.064 5.924-6.812C22.508 3.646 27.055-.58 29.51.16Z"/><path fill="url(#d)" d="M34.055 55.455c-6.273-11.66-3.153-19.734-3.153-19.734.715-.075 11.192-5.641 11.83-6.121 1.412-1.067 5.236-5.7 2.073-6.91-2.021-.771-4.441-.057-6.563-1.245-3.792-2.126-3.95-6.061-8.381-8.277-3.587-1.795-7.465-2.043-7.465-2.043s.6-9.615-.919-10.864c-1.648-1.358-4.959.452-9.357 5.033-3.4 3.544-5.016 6.072-7.412 10.747C1.868 21.581.601 27.373.235 33.545c-.513 8.664-1.113 18.883 1.124 27.44 3.895.319 32.918-4.406 32.692-5.523l.003-.007Z"/><path fill="url(#e)" d="M34.384 55.587c-.732-.456-6.172-10.187-3.479-19.882.502.076 11.185-5.626 11.823-6.11.848-.64 2.565-2.568 3.118-4.266l-3.024-1.376c.122.299-6.165 5.272-14.743 2.876-3.608-1.009-7.717-2.37-11.508-2.132-8.438.524-11.062 3.827-10.2 5.044.56.79 2.56-.959 2.168-.269-.273.481-3.562 2.237-2.75 3.515.811 1.279 3.277-.732 3.235-.162-.04.546-2.833 1.94-2.044 2.916.931 1.153 4.643-2.039 6.819-.947 5.2 2.606-5.087 14.85-.962 24.416.37.854 22.71-2.91 21.555-3.627l-.008.004Z" opacity=".6"/><path fill="url(#f)" d="M32.294 27.476c-.391.018 1.724 3.328 6.187 4.581 1.95-.955 3.917-2.209 4.251-2.46 1.411-1.065 5.235-5.698 2.072-6.908-1.192-.456-2.525-.395-3.85-.513-4.254 1.67-3.073 5.066-8.663 5.3h.003Z"/><path fill="url(#g)" d="M32.27 52.086s-3.698-8.617-1.303-16.348c-3.393.345-6.078 3.06-7.87 5.76-1.56 2.348-4.158 7.16-3.337 10.14.866 3.145 12.51.452 12.51.452v-.004Z" opacity=".97"/><path fill="url(#h)" d="M29.524 21.908c.247.223.47-.254.255-.549-.506-.697-1.264-1.4-2.348-1.562-1.311-.198-2.172.384-2.733 1.052-.212.254.043.782.287.596.69-.535 1.638-.948 2.765-.6.69.215 1.297.636 1.774 1.063Z"/><path fill="#200041" d="M44.805 22.688a5.445 5.445 0 0 0-.954-.262c-.21.21-.356.476-.424.765-.155.736.491 2.162 1.914 2 .205-.024.405-.081.592-.17.24-1.004.018-1.895-1.13-2.333h.002Z"/></g><defs><linearGradient id="b" x1="36.079" x2="49.307" y1="2.531" y2="13.626" gradientUnits="userSpaceOnUse"><stop stop-color="#E752FF"/><stop offset=".11" stop-color="#DD4FFF"/><stop offset=".28" stop-color="#C347FF"/><stop offset=".51" stop-color="#983BFF"/><stop offset=".77" stop-color="#5E2AFF"/><stop offset="1" stop-color="#271AFF"/></linearGradient><linearGradient id="c" x1="26.026" x2="17.829" y1=".961" y2="23.614" gradientUnits="userSpaceOnUse"><stop offset=".01" stop-color="#FE5B15"/><stop offset=".39" stop-color="#E83C38"/><stop offset="1" stop-color="#FB2872"/></linearGradient><linearGradient id="d" x1="10.977" x2="32.239" y1="-4.931" y2="74.428" gradientUnits="userSpaceOnUse"><stop stop-color="#FC3953"/><stop offset=".12" stop-color="#FE561F"/><stop offset=".15" stop-color="#FE7112"/><stop offset=".19" stop-color="#FE8808"/><stop offset=".22" stop-color="#FE9702"/><stop offset=".25" stop-color="#FF9C00"/><stop offset=".36" stop-color="#F90"/><stop offset=".42" stop-color="#FF9100"/><stop offset=".48" stop-color="#FF8200"/><stop offset=".52" stop-color="#FF6E00"/><stop offset=".54" stop-color="#F60"/><stop offset="1" stop-color="#FB2872"/></linearGradient><linearGradient id="e" x1="24.845" x2="41.651" y1="24.447" y2="108.48" gradientUnits="userSpaceOnUse"><stop offset=".12" stop-color="#FFEB49"/><stop offset=".36" stop-color="#FFB52B" stop-opacity=".6"/><stop offset=".58" stop-color="#FF8A14" stop-opacity=".28"/><stop offset=".73" stop-color="#FF7005" stop-opacity=".08"/><stop offset=".8" stop-color="#F60" stop-opacity="0"/></linearGradient><linearGradient id="f" x1="35.741" x2="45.045" y1="23.144" y2="30.686" gradientUnits="userSpaceOnUse"><stop offset=".23" stop-color="#FFC638"/><stop offset="1" stop-color="#FFE85D"/></linearGradient><linearGradient id="g" x1="28.785" x2="37.633" y1="44.787" y2="29.027" gradientUnits="userSpaceOnUse"><stop offset=".11" stop-color="#FB2872" stop-opacity="0"/><stop offset=".21" stop-color="#F62670" stop-opacity=".05"/><stop offset=".38" stop-color="#EB206A" stop-opacity=".18"/><stop offset=".58" stop-color="#D81762" stop-opacity=".41"/><stop offset=".81" stop-color="#BE0B57" stop-opacity=".71"/><stop offset="1" stop-color="#A5004C"/></linearGradient><linearGradient id="h" x1="31.371" x2="26.467" y1="25.032" y2="18.22" gradientUnits="userSpaceOnUse"><stop offset=".16" stop-color="#A030B9"/><stop offset=".88" stop-color="#00073A"/></linearGradient><clipPath id="a"><path fill="#fff" d="M0 0h50v40H0z"/></clipPath></defs></svg>`)}`;

const KIT_CONCERNED_SVG = `data:image/svg+xml,${encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="50" height="40" fill="none"><g clip-path="url(#a)"><path fill="url(#b)" d="M1.922 30.304c.01.067-.048.155-.211.279l-.002-.001c-.445.338-1.745 1.147-1.706 2.427.048 1.596 2.905.358 3.142 1.122.204.657-1.16 1.136-.707 1.923.866 1.505 4.237-.034 6.092 1.137 3.249 2.051 1.34 5.125-.292 8.605-.705 1.503-1.505 2.977-2.121 4.796 1.051.224 2.087.406 3.121.563 8.611 1.304 16.571.868 21.74.212 2.788-.353 4.792-.793 5.582-1.007.004 0 .445-3.11.655-4.41.738-4.58 3.894-10.886 6.772-14.095 5.403-6.02 6.2-4.493 5.862-6.296-.135-.717-1.733-.714-1.881-1.428-.108-.523 2.115-.483 1.818-1.615-.334-1.271-2.177-.812-2.808-1.13-6.035 1.22-10.764-.046-16.144 1.13l-6.384 7.831c-7.323-2.085-13.194-2.489-22.528-.043Z"/><path fill="url(#c)" d="M1.706 30.587c.163-.124.22-.212.212-.28 9.335-2.445 15.207-2.04 22.532.044 4.664 1.328 16.838-7.81 22.532-8.96.632.317 2.474-.142 2.809 1.129.297 1.132-1.927 1.092-1.818 1.614.147.715 1.746.712 1.88 1.429.339 1.803-.458.275-5.862 6.297-2.88 3.208-6.035 9.514-6.773 14.093-.206 1.281-.673 4.404-.673 4.404s-.207.063-.582.144c-.243.053-.899.207-1.9.388-.808.146-1.84.307-3.065.462-5.449.69-14.672 1.242-24.564-.672a4.47 4.47 0 0 1-.357-.094s.245-.693.66-1.638c.458-1.044 1.104-2.382 1.472-3.167 1.63-3.48 3.476-6.51.32-8.584-1.833-1.206-5.227.367-6.093-1.137-.453-.787.91-1.266.707-1.923-.237-.765-3.094.474-3.142-1.122-.04-1.28 1.261-2.09 1.706-2.427Z" opacity=".6"/><path fill="url(#d)" d="M.83 29.235c.347-1.823 3.68-2.746 5.362-4.788.986-1.197.866-4.897.918-6.282l.002-.063c.081-2.104.256-3.778.689-7.648.41-3.669 1.445-6.641 3.002-7.312 1.445-.623 3.476 1.116 6.285 4.323 1.662 1.896 3.239 4.025 3.335 4.134.153.175.383.285.985.259.133-.006.243-.026.337-.062.733-.284.371-1.607.901-5.618C23.16 2.291 24.14-.01 25.934 0c1.559.01 4.506 3.198 6.838 6.15 1.931 2.446 2.082 2.7 2.828 3.577.872 1.023 2.346 2.968 3.825 4.733 1.347 1.607 2.7 3.067 3.605 3.544 2.413 1.275 3.794.538 4.606 1.808.727 1.136-1.057 1.17-.797 1.476.035.041.084.072.14.1-4.067.823-5.87 5.127-7.557 4.225-.464-.951-1.02-1.586-1.696-1.968-.966-.546-2.179-.583-3.723-.302-2.294.417-3.988 2.818-6.1 5.311-.232.276-.46.555-.676.838a1.826 1.826 0 0 0-.225.389c-.643.758-.957.932-1.513.774-7.323-2.085-14.234-2.797-23.568-.351-.038-.284-1.252-.235-1.092-1.07Z"/><path fill="url(#e)" d="M18.471 23.301s4.58-2.436 6.133-3.116c1.583-.692 2.715-1.49 3.463-1.929 1.83-1.071.157-4.833 3.874-5.969 3.562-1.088 12.53 4.224 6.858 10.322-5.671 6.098-17.15 7.048-19.224 5.096-2.074-1.951-1.165-4.16-1.104-4.404Z" opacity=".7"/><path fill="url(#f)" d="M36.956 14.155c-1.635-1.635-3.991-2.872-6.118-1.585-2.126 1.286-2.13 4.167-1.734 5.501.396 1.335 1.236 3.651 1.781 4.196.545.544 4.072-1.253 6.001-2.638 1.93-1.385 2.989-2.556.07-5.473v-.001Z" opacity=".7"/><path fill="url(#g)" d="M33.975 12.238c-1.027-.318-2.109-.288-3.136.333a3.41 3.41 0 0 0-.319.221c-3.286-.594-7.399-.901-8.776-.992.733-.284.372-1.607.901-5.618.513-3.887 1.494-6.189 3.289-6.178 1.558.01 4.506 3.198 6.838 6.15 1.93 2.446 2.081 2.7 2.828 3.577.871 1.023 2.345 2.968 3.824 4.733l-.95-.037c-1.31-1.15-3.011-1.937-4.499-2.19Z"/><path fill="url(#h)" d="M7.112 18.105c.081-2.104.256-3.778.688-7.648.41-3.669 1.446-6.641 3.003-7.312 1.445-.623 3.476 1.116 6.284 4.322 1.663 1.897 2.078 2.46 3.064 3.75.109.142.175.275.27.385a340.715 340.715 0 0 0-5.438 2.133c-3.515 1.418-6.46 3.362-7.872 4.369h.001Z"/><path fill="url(#i)" d="M23.575 25.516c-.9.3-2.062-.132-2.606-2.234-.08-.311-.285-.89-.123-1.063.321-.347 1.088-.668 2.25-1.212.376-.176.793-.461.964-.396.286.11.451.664.735 1.81.515 2.074-.553 2.873-1.22 3.095Z"/><path fill="#fff" d="M23.336 23.423a.68.68 0 1 1 1.336-.251.68.68 0 0 1-1.336.25Z"/><path fill="url(#j)" d="M34.57 15.462c1.077-.037 1.933 1.163 2.522 2.903.123.362.189.677.213.953.108 1.227-.629 1.671-1.158 1.847-.319.105-.923.227-1.537-.125-.47-.27-.945-.817-1.3-1.866-.78-2.297-.539-3.651 1.26-3.712Z"/><path fill="#fff" d="M36.005 18.657a.653.653 0 1 1 .347 1.258.653.653 0 0 1-.347-1.258Z"/><path fill="#FFC635" d="M26.863 28.348c2.11-2.493 4.844-4.587 7.138-5.004 1.545-.28 2.757-.244 3.724.302.677.382 1.233 1.017 1.695 1.968.027.055.055.105.08.162 1.274 2.778.637 7.178-5.586 8.539-3.453.755-8.996-2.319-7.954-4.74.057-.131.128-.261.225-.389.216-.283.445-.562.678-.838Z"/><path fill="#00073A" d="M35.591 26.513c-1.43.12-2.343-.987-2.209-1.665.095-.482.608-1.086 1.69-1.174 1.224-.1 1.933.367 2.164.838.286.58-.14 1.875-1.645 2Z"/></g><defs><linearGradient id="b" x1="25.145" x2="24.446" y1="6.967" y2="91.615" gradientUnits="userSpaceOnUse"><stop stop-color="#F60"/><stop offset=".207" stop-color="#FF9C00"/><stop offset=".519" stop-color="#F60"/><stop offset=".856" stop-color="#FB2872"/></linearGradient><linearGradient id="c" x1="24.234" x2="31.416" y1="23.247" y2="72.496" gradientUnits="userSpaceOnUse"><stop offset=".151" stop-color="#FFEB49"/><stop offset=".343" stop-color="#FFC735" stop-opacity=".73"/><stop offset=".581" stop-color="#FF9D1E" stop-opacity=".421"/><stop offset=".778" stop-color="#FF7F0E" stop-opacity=".194"/><stop offset=".923" stop-color="#FF6D03" stop-opacity=".053"/><stop offset="1" stop-color="#F60" stop-opacity="0"/></linearGradient><linearGradient id="d" x1="24.162" x2="24.65" y1="6.606" y2="65.617" gradientUnits="userSpaceOnUse"><stop stop-color="#FE5B15"/><stop offset=".075" stop-color="#FE6F0E"/><stop offset=".213" stop-color="#FE8F03"/><stop offset=".289" stop-color="#FF9C00"/><stop offset=".519" stop-color="#F60"/><stop offset=".856" stop-color="#FB2872"/></linearGradient><linearGradient id="g" x1="29.976" x2="25.888" y1="10.934" y2="-3.838" gradientUnits="userSpaceOnUse"><stop stop-color="#F60" stop-opacity="0"/><stop offset=".016" stop-color="#F60" stop-opacity=".172"/><stop offset=".036" stop-color="#F60" stop-opacity=".364"/><stop offset=".057" stop-color="#F60" stop-opacity=".535"/><stop offset=".079" stop-color="#F60" stop-opacity=".679"/><stop offset=".102" stop-color="#F60" stop-opacity=".796"/><stop offset=".125" stop-color="#F60" stop-opacity=".886"/><stop offset=".151" stop-color="#F60" stop-opacity=".95"/><stop offset=".18" stop-color="#F60" stop-opacity=".988"/><stop offset=".217" stop-color="#F60"/><stop offset=".611" stop-color="#FD4737"/><stop offset=".995" stop-color="#FB2872"/></linearGradient><linearGradient id="h" x1="13.304" x2="8.292" y1="13.683" y2="1.022" gradientUnits="userSpaceOnUse"><stop stop-color="#F60" stop-opacity="0"/><stop offset=".029" stop-color="#F60" stop-opacity=".172"/><stop offset=".067" stop-color="#F60" stop-opacity=".364"/><stop offset=".106" stop-color="#F60" stop-opacity=".535"/><stop offset=".147" stop-color="#F60" stop-opacity=".679"/><stop offset=".189" stop-color="#F60" stop-opacity=".796"/><stop offset=".234" stop-color="#F60" stop-opacity=".886"/><stop offset=".282" stop-color="#F60" stop-opacity=".95"/><stop offset=".335" stop-color="#F60" stop-opacity=".988"/><stop offset=".405" stop-color="#F60"/><stop offset=".706" stop-color="#FD4737"/><stop offset="1" stop-color="#FB2872"/></linearGradient><linearGradient id="i" x1="22.205" x2="23.372" y1="19.387" y2="25.513" gradientUnits="userSpaceOnUse"><stop offset=".157" stop-color="#A030B9"/><stop offset=".875" stop-color="#00073A"/></linearGradient><linearGradient id="j" x1="34.417" x2="35.482" y1="13.835" y2="20.897" gradientUnits="userSpaceOnUse"><stop offset=".157" stop-color="#A030B9"/><stop offset=".875" stop-color="#00073A"/></linearGradient><radialGradient id="e" cx="0" cy="0" r="1" gradientTransform="matrix(-8.68143 0 0 -10.9212 21.594 14.586)" gradientUnits="userSpaceOnUse"><stop stop-color="#D81F60" stop-opacity=".5"/><stop offset=".221" stop-color="#D81F60" stop-opacity=".486"/><stop offset=".389" stop-color="#D81F60" stop-opacity=".441"/><stop offset=".541" stop-color="#D81F60" stop-opacity=".366"/><stop offset=".681" stop-color="#D81F60" stop-opacity=".259"/><stop offset=".814" stop-color="#D81F60" stop-opacity=".123"/><stop offset=".91" stop-color="#D81F60" stop-opacity="0"/></radialGradient><radialGradient id="f" cx="0" cy="0" r="1" gradientTransform="rotate(180 17.005 10.255) scale(8.63633)" gradientUnits="userSpaceOnUse"><stop offset=".628" stop-color="#D81F60" stop-opacity="0"/><stop offset=".704" stop-color="#D81F60" stop-opacity=".017"/><stop offset=".775" stop-color="#D81F60" stop-opacity=".069"/><stop offset=".843" stop-color="#D81F60" stop-opacity=".156"/><stop offset=".911" stop-color="#D81F60" stop-opacity=".279"/><stop offset=".976" stop-color="#D81F60" stop-opacity=".435"/><stop offset="1" stop-color="#D81F60" stop-opacity=".5"/></radialGradient><clipPath id="a"><path fill="#fff" d="M0 0h50v40H0z"/></clipPath></defs></svg>`)}`;

// Pre-load Kit images
function useKitImages() {
  const [images, setImages] = useState({ happy: null, concerned: null });

  useEffect(() => {
    const happy = new Image();
    const concerned = new Image();
    let loaded = 0;
    const onLoad = () => {
      loaded++;
      if (loaded === 2) {
        setImages({ happy, concerned });
      }
    };
    happy.onload = onLoad;
    concerned.onload = onLoad;
    happy.src = KIT_HAPPY_SVG;
    concerned.src = KIT_CONCERNED_SVG;
  }, []);

  return images;
}

// --- Canvas Renderer ---
function renderGame(canvas, gameState, kitImages, isWin) {
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    return;
  }

  const container = canvas.parentElement;
  if (!container) {
    return;
  }

  const availableWidth = container.clientWidth;
  const availableHeight = container.clientHeight;
  const padding = 20;
  const maxCellW = Math.floor((availableWidth - padding) / gameState.width);
  const maxCellH = Math.floor((availableHeight - padding) / gameState.height);
  const cellSize = Math.max(Math.min(maxCellW, maxCellH, 80), 20);

  const width = gameState.width * cellSize;
  const height = gameState.height * cellSize;
  canvas.width = width;
  canvas.height = height;

  // Background
  ctx.fillStyle = "#2a2a2a";
  ctx.fillRect(0, 0, width, height);

  // Floor grid
  for (let y = 0; y < gameState.height; y++) {
    for (let x = 0; x < gameState.width; x++) {
      ctx.fillStyle = "#3a3a3a";
      ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
      ctx.strokeStyle = "#333";
      ctx.lineWidth = 0.5;
      ctx.strokeRect(x * cellSize, y * cellSize, cellSize, cellSize);
    }
  }

  // Walls - brick-like pattern
  gameState.walls.forEach(wall => {
    const x = wall.x * cellSize;
    const y = wall.y * cellSize;
    ctx.fillStyle = "#5a4a3a";
    ctx.fillRect(x, y, cellSize, cellSize);
    ctx.strokeStyle = "#4a3a2a";
    ctx.lineWidth = 1.5;
    ctx.strokeRect(x + 1, y + 1, cellSize - 2, cellSize - 2);
    // Brick lines
    ctx.strokeStyle = "#6a5a4a";
    ctx.lineWidth = 0.5;
    ctx.beginPath();
    ctx.moveTo(x, y + cellSize * 0.33);
    ctx.lineTo(x + cellSize, y + cellSize * 0.33);
    ctx.moveTo(x, y + cellSize * 0.66);
    ctx.lineTo(x + cellSize, y + cellSize * 0.66);
    ctx.moveTo(x + cellSize * 0.5, y);
    ctx.lineTo(x + cellSize * 0.5, y + cellSize * 0.33);
    ctx.moveTo(x + cellSize * 0.25, y + cellSize * 0.33);
    ctx.lineTo(x + cellSize * 0.25, y + cellSize * 0.66);
    ctx.moveTo(x + cellSize * 0.75, y + cellSize * 0.66);
    ctx.lineTo(x + cellSize * 0.75, y + cellSize);
    ctx.stroke();
  });

  // Goals - purple circles
  gameState.goals.forEach(goal => {
    const cx = goal.x * cellSize + cellSize / 2;
    const cy = goal.y * cellSize + cellSize / 2;
    ctx.fillStyle = "rgba(160, 48, 185, 0.4)";
    ctx.beginPath();
    ctx.arc(cx, cy, cellSize * 0.32, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "rgba(160, 48, 185, 0.8)";
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, cellSize * 0.32, 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillStyle = "rgba(200, 100, 220, 0.5)";
    ctx.beginPath();
    ctx.arc(cx, cy, cellSize * 0.15, 0, Math.PI * 2);
    ctx.fill();
  });

  // Boxes
  gameState.boxes.forEach(box => {
    const x = box.x * cellSize;
    const y = box.y * cellSize;
    const onGoal = gameState.goals.some(
      g => g.x === box.x && g.y === box.y
    );
    const inset = cellSize * 0.1;

    if (onGoal) {
      ctx.fillStyle = "#2d6016";
      ctx.fillRect(x + inset, y + inset, cellSize - inset * 2, cellSize - inset * 2);
      ctx.strokeStyle = "#4caf50";
      ctx.lineWidth = 2.5;
      ctx.strokeRect(x + inset, y + inset, cellSize - inset * 2, cellSize - inset * 2);
    } else {
      ctx.fillStyle = "#c47b2b";
      ctx.fillRect(x + inset, y + inset, cellSize - inset * 2, cellSize - inset * 2);
      ctx.strokeStyle = "#a0622d";
      ctx.lineWidth = 2;
      ctx.strokeRect(x + inset, y + inset, cellSize - inset * 2, cellSize - inset * 2);
      // Cross lines
      ctx.strokeStyle = "#8a5520";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x + inset, y + cellSize / 2);
      ctx.lineTo(x + cellSize - inset, y + cellSize / 2);
      ctx.moveTo(x + cellSize / 2, y + inset);
      ctx.lineTo(x + cellSize / 2, y + cellSize - inset);
      ctx.stroke();
    }
  });

  // Player (Kit face)
  const playerOnGoal = gameState.goals.some(
    g => g.x === gameState.player.x && g.y === gameState.player.y
  );
  const kitImg = playerOnGoal ? kitImages?.happy : kitImages?.concerned;
  const px = gameState.player.x * cellSize;
  const py = gameState.player.y * cellSize;

  if (kitImg) {
    const pad = cellSize * 0.05;
    ctx.drawImage(kitImg, px + pad, py + pad, cellSize - pad * 2, cellSize - pad * 2);
  } else {
    // Fallback circle
    const cx = px + cellSize / 2;
    const cy = py + cellSize / 2;
    ctx.fillStyle = playerOnGoal ? "#4caf50" : "#ff6600";
    ctx.beginPath();
    ctx.arc(cx, cy, cellSize * 0.35, 0, Math.PI * 2);
    ctx.fill();
  }

  // Win overlay
  if (isWin) {
    ctx.fillStyle = "rgba(0, 0, 0, 0.55)";
    ctx.fillRect(0, 0, width, height);

    // Draw happy Kit in the center
    const kitSize = Math.min(width, height) * 0.35;
    if (kitImages?.happy) {
      ctx.drawImage(
        kitImages.happy,
        (width - kitSize) / 2,
        height / 2 - kitSize * 0.65,
        kitSize,
        kitSize * 0.8
      );
    }

    ctx.fillStyle = "#4caf50";
    ctx.font = `bold ${Math.max(cellSize * 0.6, 14)}px system-ui, sans-serif`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText("Level Complete!", width / 2, height / 2 + kitSize * 0.3);
  }
}

// --- Main Widget Component ---
function SokobanGame({ isMaximized }) {
  const prefs = useSelector(state => state.Prefs.values);
  const widgetSize = resolveWidgetSize(sokobanEntry, prefs);
  const novaEnabled = prefs["nova.enabled"];

  const [levelIndex, setLevelIndex] = useState(0);
  const [engine, setEngine] = useState(() =>
    createEngine(MICROBAN_LEVELS[0])
  );
  const [isWin, setIsWin] = useState(false);
  const canvasRef = useRef(null);
  const containerRef = useRef(null);
  const kitImages = useKitImages();

  const draw = useCallback(() => {
    if (canvasRef.current) {
      renderGame(canvasRef.current, engine.state, kitImages, isWin);
    }
  }, [engine.state, kitImages, isWin]);

  useEffect(() => {
    draw();
  }, [draw]);

  useEffect(() => {
    const handleResize = () => draw();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, [draw]);

  const loadLevel = useCallback(idx => {
    const clamped = Math.max(0, Math.min(idx, MICROBAN_LEVELS.length - 1));
    setLevelIndex(clamped);
    setEngine(createEngine(MICROBAN_LEVELS[clamped]));
    setIsWin(false);
  }, []);

  const handleMove = useCallback(
    direction => {
      if (isWin) {
        return;
      }
      const result = movePlayer(engine, direction);
      if (result.valid) {
        setEngine(result.engine);
        if (result.isWin) {
          setIsWin(true);
        }
      }
    },
    [engine, isWin]
  );

  const handleUndo = useCallback(() => {
    if (!isWin) {
      setEngine(e => undoMove(e));
    }
  }, [isWin]);

  const handleRedo = useCallback(() => {
    if (!isWin) {
      setEngine(e => redoMove(e));
    }
  }, [isWin]);

  const handleReset = useCallback(() => {
    setEngine(e => resetEngine(e));
    setIsWin(false);
  }, []);

  const handleNextLevel = useCallback(() => {
    if (levelIndex < MICROBAN_LEVELS.length - 1) {
      loadLevel(levelIndex + 1);
    }
  }, [levelIndex, loadLevel]);

  const handlePrevLevel = useCallback(() => {
    if (levelIndex > 0) {
      loadLevel(levelIndex - 1);
    }
  }, [levelIndex, loadLevel]);

  useEffect(() => {
    const handleKey = e => {
      // Only handle keys when this widget or its children are focused,
      // or when nothing specific is focused (body/document)
      const active = document.activeElement;
      const widgetEl = containerRef.current;
      if (
        active &&
        active !== document.body &&
        widgetEl &&
        !widgetEl.contains(active)
      ) {
        return;
      }

      let handled = true;
      switch (e.key) {
        case "ArrowUp":
        case "w":
          handleMove(Direction.Up);
          break;
        case "ArrowDown":
        case "s":
          handleMove(Direction.Down);
          break;
        case "ArrowLeft":
        case "a":
          handleMove(Direction.Left);
          break;
        case "ArrowRight":
        case "d":
          handleMove(Direction.Right);
          break;
        case "z":
          if (e.ctrlKey || e.metaKey) {
            if (e.shiftKey) {
              handleRedo();
            } else {
              handleUndo();
            }
          } else {
            handled = false;
          }
          break;
        case "u":
          handleUndo();
          break;
        case "r":
          handleReset();
          break;
        case "Enter":
          if (isWin) {
            handleNextLevel();
          } else {
            handled = false;
          }
          break;
        default:
          handled = false;
      }
      if (handled) {
        e.preventDefault();
      }
    };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [
    handleMove,
    handleUndo,
    handleRedo,
    handleReset,
    handleNextLevel,
    isWin,
  ]);

  return (
    <article
      ref={containerRef}
      className={`sokoban-game widget ${novaEnabled ? `col-4 ${widgetSize}-widget` : ""} ${isMaximized ? "is-maximized" : ""}`}
      tabIndex="-1"
    >
      <div className="sokoban-header">
        <span className="sokoban-title">Kit's Sokoban</span>
        <span className="sokoban-level-info">
          <button
            className="sokoban-btn"
            onClick={handlePrevLevel}
            disabled={levelIndex === 0}
            title="Previous level"
          >
            {"<"}
          </button>
          <span className="sokoban-level-num">
            {levelIndex + 1}/{MICROBAN_LEVELS.length}
          </span>
          <button
            className="sokoban-btn"
            onClick={handleNextLevel}
            disabled={levelIndex === MICROBAN_LEVELS.length - 1}
            title="Next level"
          >
            {">"}
          </button>
        </span>
        <span className="sokoban-stats">
          Moves: {engine.state.moves} | Pushes: {engine.state.pushes}
        </span>
      </div>
      <div className="sokoban-canvas-container">
        <canvas ref={canvasRef} />
      </div>
      <div className="sokoban-controls">
        <button
          className="sokoban-btn"
          onClick={handleUndo}
          disabled={engine.history.length === 0 || isWin}
          title="Undo (U / Ctrl+Z)"
        >
          Undo
        </button>
        <button
          className="sokoban-btn"
          onClick={handleRedo}
          disabled={engine.redoStack.length === 0 || isWin}
          title="Redo (Ctrl+Shift+Z)"
        >
          Redo
        </button>
        <button
          className="sokoban-btn"
          onClick={handleReset}
          title="Reset (R)"
        >
          Reset
        </button>
        {isWin && (
          <button className="sokoban-btn sokoban-btn-next" onClick={handleNextLevel}>
            Next Level
          </button>
        )}
      </div>
    </article>
  );
}

export { SokobanGame };
