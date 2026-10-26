"use strict";

const triples = [
  [1.000001, 3.14159, 10.3],
  [0.001, 0.1, 100.1],
  [0, 0, 0],
  [1, 1, 1],
  [1, 2, 4],
  [0, Number.MIN_VALUE, 2 * Number.MIN_VALUE],
  [0, Number.MAX_VALUE / 2, Number.MAX_VALUE],
];
console.log(JSON.stringify(triples.map(([begin, afterAPI, afterFlush]) => {
  const apiMs = afterAPI - begin;
  const flushMs = afterFlush - afterAPI;
  const totalMs = afterFlush - begin;
  return { begin, afterAPI, afterFlush, apiMs, flushMs, totalMs,
    roundedSum: apiMs + flushMs, exactAdditionGate: apiMs + flushMs === totalMs };
})));
