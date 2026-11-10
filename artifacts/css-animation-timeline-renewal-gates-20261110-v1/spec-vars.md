# CSS-VARIABLES-1#using-variables

**Using Cascading Variables: the var() notation** (heading)

**SHA**: hash:72c4b00afaa33f30ded58f4b1e4595c7155bb410d01e0d24b8157cdbdf101e40

## Content

The value of a [custom property](CSS-VARIABLES-1#custom-property) can be substituted into the value of another property with the [var()](CSS-VARIABLES-1#funcdef-var) function. The syntax of var() is:

```
var() = var( <custom-property-name> , <declaration-value>? )
```

The [var()](CSS-VARIABLES-1#funcdef-var) function is an [arbitrary substitution function](CSS-VALUES-5#arbitrary-substitution-function), and its [argument grammar](CSS-VALUES-5#argument-grammar) is:

```
<var-args> = var( <declaration-value> , <declaration-value>? )
```

Tests

*   [variable-reference-07.html](https://wpt.fyi/results/css/css-variables/variable-reference-07.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-07.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-07.html)
*   [variable-reference-08.html](https://wpt.fyi/results/css/css-variables/variable-reference-08.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-08.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-08.html)
*   [variable-reference-09.html](https://wpt.fyi/results/css/css-variables/variable-reference-09.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-09.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-09.html)
*   [variable-reference-10.html](https://wpt.fyi/results/css/css-variables/variable-reference-10.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-10.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-10.html)
*   [variable-reference-17.html](https://wpt.fyi/results/css/css-variables/variable-reference-17.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-17.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-17.html)
*   [variable-reference-20.html](https://wpt.fyi/results/css/css-variables/variable-reference-20.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-20.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-20.html)
*   [variable-reference-21.html](https://wpt.fyi/results/css/css-variables/variable-reference-21.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-21.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-21.html)
*   [variable-reference-22.html](https://wpt.fyi/results/css/css-variables/variable-reference-22.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-22.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-22.html)
*   [variable-reference-23.html](https://wpt.fyi/results/css/css-variables/variable-reference-23.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-23.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-23.html)
*   [variable-reference-24.html](https://wpt.fyi/results/css/css-variables/variable-reference-24.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-24.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-24.html)
*   [variable-reference-25.html](https://wpt.fyi/results/css/css-variables/variable-reference-25.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-25.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-25.html)
*   [variable-reference-28.html](https://wpt.fyi/results/css/css-variables/variable-reference-28.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-28.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-28.html)
*   [variable-reference-29.html](https://wpt.fyi/results/css/css-variables/variable-reference-29.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-29.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-29.html)
*   [variable-reference-31.html](https://wpt.fyi/results/css/css-variables/variable-reference-31.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-31.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-31.html)
*   [variable-reference-32.html](https://wpt.fyi/results/css/css-variables/variable-reference-32.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-32.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-32.html)
*   [variable-reference-33.html](https://wpt.fyi/results/css/css-variables/variable-reference-33.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-33.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-33.html)
*   [variable-reference-34.html](https://wpt.fyi/results/css/css-variables/variable-reference-34.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-34.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-34.html)
*   [variable-reference-35.html](https://wpt.fyi/results/css/css-variables/variable-reference-35.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-35.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-35.html)
*   [variable-reference.html](https://wpt.fyi/results/css/css-variables/variable-reference.html) [(live test)](http://wpt.live/css/css-variables/variable-reference.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference.html)

@supports

*   [variable-supports-01.html](https://wpt.fyi/results/css/css-variables/variable-supports-01.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-01.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-01.html)
*   [variable-supports-02.html](https://wpt.fyi/results/css/css-variables/variable-supports-02.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-02.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-02.html)
*   [variable-supports-03.html](https://wpt.fyi/results/css/css-variables/variable-supports-03.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-03.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-03.html)
*   [variable-supports-04.html](https://wpt.fyi/results/css/css-variables/variable-supports-04.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-04.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-04.html)
*   [variable-supports-05.html](https://wpt.fyi/results/css/css-variables/variable-supports-05.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-05.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-05.html)
*   [variable-supports-06.html](https://wpt.fyi/results/css/css-variables/variable-supports-06.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-06.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-06.html)
*   [variable-supports-07.html](https://wpt.fyi/results/css/css-variables/variable-supports-07.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-07.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-07.html)
*   [variable-supports-08.html](https://wpt.fyi/results/css/css-variables/variable-supports-08.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-08.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-08.html)
*   [variable-supports-09.html](https://wpt.fyi/results/css/css-variables/variable-supports-09.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-09.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-09.html)
*   [variable-supports-10.html](https://wpt.fyi/results/css/css-variables/variable-supports-10.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-10.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-10.html)
*   [variable-supports-11.html](https://wpt.fyi/results/css/css-variables/variable-supports-11.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-11.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-11.html)
*   [variable-supports-12.html](https://wpt.fyi/results/css/css-variables/variable-supports-12.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-12.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-12.html)
*   [variable-supports-13.html](https://wpt.fyi/results/css/css-variables/variable-supports-13.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-13.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-13.html)
*   [variable-supports-14.html](https://wpt.fyi/results/css/css-variables/variable-supports-14.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-14.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-14.html)
*   [variable-supports-15.html](https://wpt.fyi/results/css/css-variables/variable-supports-15.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-15.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-15.html)
*   [variable-supports-16.html](https://wpt.fyi/results/css/css-variables/variable-supports-16.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-16.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-16.html)
*   [variable-supports-17.html](https://wpt.fyi/results/css/css-variables/variable-supports-17.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-17.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-17.html)
*   [variable-supports-18.html](https://wpt.fyi/results/css/css-variables/variable-supports-18.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-18.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-18.html)
*   [variable-supports-19.html](https://wpt.fyi/results/css/css-variables/variable-supports-19.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-19.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-19.html)
*   [variable-supports-20.html](https://wpt.fyi/results/css/css-variables/variable-supports-20.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-20.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-20.html)
*   [variable-supports-21.html](https://wpt.fyi/results/css/css-variables/variable-supports-21.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-21.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-21.html)
*   [variable-supports-22.html](https://wpt.fyi/results/css/css-variables/variable-supports-22.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-22.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-22.html)
*   [variable-supports-23.html](https://wpt.fyi/results/css/css-variables/variable-supports-23.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-23.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-23.html)
*   [variable-supports-24.html](https://wpt.fyi/results/css/css-variables/variable-supports-24.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-24.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-24.html)
*   [variable-supports-25.html](https://wpt.fyi/results/css/css-variables/variable-supports-25.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-25.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-25.html)
*   [variable-supports-26.html](https://wpt.fyi/results/css/css-variables/variable-supports-26.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-26.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-26.html)
*   [variable-supports-27.html](https://wpt.fyi/results/css/css-variables/variable-supports-27.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-27.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-27.html)
*   [variable-supports-28.html](https://wpt.fyi/results/css/css-variables/variable-supports-28.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-28.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-28.html)
*   [variable-supports-29.html](https://wpt.fyi/results/css/css-variables/variable-supports-29.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-29.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-29.html)
*   [variable-supports-30.html](https://wpt.fyi/results/css/css-variables/variable-supports-30.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-30.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-30.html)
*   [variable-supports-31.html](https://wpt.fyi/results/css/css-variables/variable-supports-31.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-31.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-31.html)
*   [variable-supports-32.html](https://wpt.fyi/results/css/css-variables/variable-supports-32.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-32.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-32.html)
*   [variable-supports-33.html](https://wpt.fyi/results/css/css-variables/variable-supports-33.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-33.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-33.html)
*   [variable-supports-34.html](https://wpt.fyi/results/css/css-variables/variable-supports-34.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-34.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-34.html)
*   [variable-supports-35.html](https://wpt.fyi/results/css/css-variables/variable-supports-35.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-35.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-35.html)
*   [variable-supports-36.html](https://wpt.fyi/results/css/css-variables/variable-supports-36.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-36.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-36.html)
*   [variable-supports-37.html](https://wpt.fyi/results/css/css-variables/variable-supports-37.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-37.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-37.html)
*   [variable-supports-38.html](https://wpt.fyi/results/css/css-variables/variable-supports-38.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-38.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-38.html)
*   [variable-supports-39.html](https://wpt.fyi/results/css/css-variables/variable-supports-39.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-39.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-39.html)
*   [variable-supports-40.html](https://wpt.fyi/results/css/css-variables/variable-supports-40.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-40.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-40.html)
*   [variable-supports-41.html](https://wpt.fyi/results/css/css-variables/variable-supports-41.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-41.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-41.html)
*   [variable-supports-42.html](https://wpt.fyi/results/css/css-variables/variable-supports-42.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-42.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-42.html)
*   [variable-supports-43.html](https://wpt.fyi/results/css/css-variables/variable-supports-43.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-43.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-43.html)
*   [variable-supports-44.html](https://wpt.fyi/results/css/css-variables/variable-supports-44.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-44.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-44.html)
*   [variable-supports-45.html](https://wpt.fyi/results/css/css-variables/variable-supports-45.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-45.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-45.html)
*   [variable-supports-46.html](https://wpt.fyi/results/css/css-variables/variable-supports-46.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-46.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-46.html)
*   [variable-supports-47.html](https://wpt.fyi/results/css/css-variables/variable-supports-47.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-47.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-47.html)
*   [variable-supports-48.html](https://wpt.fyi/results/css/css-variables/variable-supports-48.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-48.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-48.html)
*   [variable-supports-49.html](https://wpt.fyi/results/css/css-variables/variable-supports-49.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-49.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-49.html)
*   [variable-supports-50.html](https://wpt.fyi/results/css/css-variables/variable-supports-50.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-50.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-50.html)
*   [variable-supports-51.html](https://wpt.fyi/results/css/css-variables/variable-supports-51.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-51.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-51.html)
*   [variable-supports-52.html](https://wpt.fyi/results/css/css-variables/variable-supports-52.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-52.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-52.html)
*   [variable-supports-53.html](https://wpt.fyi/results/css/css-variables/variable-supports-53.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-53.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-53.html)
*   [variable-supports-54.html](https://wpt.fyi/results/css/css-variables/variable-supports-54.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-54.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-54.html)
*   [variable-supports-55.html](https://wpt.fyi/results/css/css-variables/variable-supports-55.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-55.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-55.html)
*   [variable-supports-56.html](https://wpt.fyi/results/css/css-variables/variable-supports-56.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-56.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-56.html)
*   [variable-supports-57.html](https://wpt.fyi/results/css/css-variables/variable-supports-57.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-57.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-57.html)
*   [variable-supports-58.html](https://wpt.fyi/results/css/css-variables/variable-supports-58.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-58.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-58.html)
*   [variable-supports-59.html](https://wpt.fyi/results/css/css-variables/variable-supports-59.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-59.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-59.html)
*   [variable-supports-60.html](https://wpt.fyi/results/css/css-variables/variable-supports-60.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-60.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-60.html)
*   [variable-supports-61.html](https://wpt.fyi/results/css/css-variables/variable-supports-61.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-61.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-61.html)
*   [variable-supports-62.html](https://wpt.fyi/results/css/css-variables/variable-supports-62.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-62.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-62.html)
*   [variable-supports-63.html](https://wpt.fyi/results/css/css-variables/variable-supports-63.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-63.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-63.html)
*   [variable-supports-64.html](https://wpt.fyi/results/css/css-variables/variable-supports-64.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-64.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-64.html)
*   [variable-supports-65.html](https://wpt.fyi/results/css/css-variables/variable-supports-65.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-65.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-65.html)
*   [variable-supports-66.html](https://wpt.fyi/results/css/css-variables/variable-supports-66.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-66.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-66.html)
*   [variable-supports-67.html](https://wpt.fyi/results/css/css-variables/variable-supports-67.html) [(live test)](http://wpt.live/css/css-variables/variable-supports-67.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-supports-67.html)

* * *

The first argument to the function is the name of the [custom property](CSS-VARIABLES-1#custom-property) to be substituted. The second argument to the function, if provided, is a fallback value, which is used as the substitution value when the value of the referenced custom property is the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value).

Tests

*   [variable-declaration-08.html](https://wpt.fyi/results/css/css-variables/variable-declaration-08.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-08.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-08.html)
*   [variable-declaration-09.html](https://wpt.fyi/results/css/css-variables/variable-declaration-09.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-09.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-09.html)
*   [variable-declaration-10.html](https://wpt.fyi/results/css/css-variables/variable-declaration-10.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-10.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-10.html)
*   [variable-declaration-11.html](https://wpt.fyi/results/css/css-variables/variable-declaration-11.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-11.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-11.html)
*   [variable-declaration-12.html](https://wpt.fyi/results/css/css-variables/variable-declaration-12.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-12.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-12.html)
*   [variable-declaration-13.html](https://wpt.fyi/results/css/css-variables/variable-declaration-13.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-13.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-13.html)
*   [variable-declaration-22.html](https://wpt.fyi/results/css/css-variables/variable-declaration-22.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-22.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-22.html)

In an exception to the usual [comma elision rules](CSS-VALUES-4#comb-comma), which require commas to be omitted when they’re not separating values, a bare comma, with nothing following it, must be treated as valid in [var()](CSS-VARIABLES-1#funcdef-var), indicating an empty fallback value.

Tests

*   [variable-declaration-07.html](https://wpt.fyi/results/css/css-variables/variable-declaration-07.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-07.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-07.html)
*   [variable-declaration-37.html](https://wpt.fyi/results/css/css-variables/variable-declaration-37.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-37.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-37.html)
*   [variable-reference-06.html](https://wpt.fyi/results/css/css-variables/variable-reference-06.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-06.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-06.html)
*   [variable-reference-11.html](https://wpt.fyi/results/css/css-variables/variable-reference-11.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-11.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-11.html)
*   [variable-reference-26.html](https://wpt.fyi/results/css/css-variables/variable-reference-26.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-26.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-26.html)
*   [variable-reference-27.html](https://wpt.fyi/results/css/css-variables/variable-reference-27.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-27.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-27.html)

> **Note:** Note: That is, var(--a,) is a valid function, specifying that if the --a custom property is invalid or missing, the [var()](CSS-VARIABLES-1#funcdef-var) should be replaced with nothing.

> **Note:** Note: The syntax of the fallback, like that of [custom properties](CSS-VARIABLES-1#custom-property), allows commas. For example, var(--foo, red, blue) defines a fallback of red, blue; that is, anything between the first comma and the end of the function is considered a fallback value.

> **Example:** The fallback value allows for some types of defensive coding. For example, an author may create a component intended to be included in a larger application, and use variables to style it so that it’s easy for the author of the larger application to theme the component to match the rest of the app.Without fallback, the app author must supply a value for every variable that your component uses. With fallback, the component author can supply defaults, so the app author only needs to supply values for the variables they wish to override.
>
> ```
> /* In the component's style: */
> .component .header {
>   color: var(--header-color, blue);
> }
> .component .text {
>   color: var(--text-color, black);
> }
>
> /* In the larger application's style: */
> .component {
>   --text-color: #080;
>   /* header-color isn't set,
>      and so remains blue,
>      the fallback value */
> }
> ```

To **[replace a var() function](CSS-VALUES-5#replace-an-arbitrary-substitution-function)**, given a list of *arguments*:

1.  Let *el* be the element that the style containing the [var()](CSS-VARIABLES-1#funcdef-var) function is being applied to. Let *first arg* be the first [\<declaration-value>](CSS-SYNTAX-3#typedef-declaration-value) in *arguments*. Let *second arg* be the \<declaration-value>? passed after the comma, or null if there was no comma.

2.  [Substitute arbitrary substitution functions](CSS-VALUES-5#substitute-arbitrary-substitution-function) in *first arg*, then [parse](CSS-SYNTAX-3#css-parse-something-according-to-a-css-grammar) it as a [\<custom-property-name>](CSS-VARIABLES-1#typedef-custom-property-name). If parsing returned a \<custom-property-name>, let *result* be the [computed value](CSS-CASCADE-5#computed-value) of the corresponding [custom property](CSS-VARIABLES-1#custom-property) on *el*. Otherwise, let *result* be the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value).

    > **Note:** Note: Determining the [computed value](CSS-CASCADE-5#computed-value) for the [custom property](CSS-VARIABLES-1#custom-property) implies that [property replacement](CSS-VALUES-5#property-replacement) takes place, which may cause a [cycle](CSS-VALUES-5#cyclic-substitution-contexts).

3.  If the [custom property](CSS-VARIABLES-1#custom-property) named by the [var()](CSS-VARIABLES-1#funcdef-var)’s first argument is [animation-tainted](CSS-VARIABLES-1#animation-tainted), and the var() is being used in a property that is [not animatable](WEB-ANIMATIONS-1#not-animatable), set *result* to the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value).

4.  If *result* contains the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value), and *second arg* was provided, set *result* to the result of [substitute arbitrary substitution functions](CSS-VALUES-5#substitute-arbitrary-substitution-function) on *second arg*.

5.  Return *result*.

> **Example:** Due to [property replacement](CSS-VALUES-5#property-replacement), [custom properties](CSS-VARIABLES-1#custom-property) can form [cycles](CSS-VALUES-5#cyclic-substitution-contexts):
>
> ```
> :root {
>   --one: calc(var(--two) + 20px);
>   --two: calc(var(--one) - 20px);
> }
> ```
>
> In the above, both --one and --two compute to the [guaranteed-invalid value](CSS-VARIABLES-1#guaranteed-invalid-value), since their [substitution contexts](CSS-VALUES-5#substitution-context) have been marked as cyclic.

Tests

*   [variable-cycles.html](https://wpt.fyi/results/css/css-variables/variable-cycles.html) [(live test)](http://wpt.live/css/css-variables/variable-cycles.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-cycles.html)
*   [variable-declaration-30.html](https://wpt.fyi/results/css/css-variables/variable-declaration-30.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-30.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-30.html)
*   [variable-declaration-48.html](https://wpt.fyi/results/css/css-variables/variable-declaration-48.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-48.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-48.html)
*   [variable-declaration-49.html](https://wpt.fyi/results/css/css-variables/variable-declaration-49.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-49.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-49.html)
*   [variable-declaration-50.html](https://wpt.fyi/results/css/css-variables/variable-declaration-50.html) [(live test)](http://wpt.live/css/css-variables/variable-declaration-50.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-declaration-50.html)
*   [variable-reference-39.html](https://wpt.fyi/results/css/css-variables/variable-reference-39.html) [(live test)](http://wpt.live/css/css-variables/variable-reference-39.html) [(source)](https://github.com/web-platform-tests/wpt/blob/master/css/css-variables/variable-reference-39.html)

> **Example:** Note that the [custom property](CSS-VARIABLES-1#custom-property) name looked up by a [var()](CSS-VARIABLES-1#funcdef-var) may itself come from a var() function:
>
> ```
> :root {
>   --other: 10px;
>   --myvar: --other;
>   --result: var(var(--myvar));
> }
> ```
>
> Since the inner var() is resolved before the outer var(), the computed value of --result becomes 10px.

## Navigation

- Prev: `defining-variables` — Defining Custom Properties: the --* family of properties
- Next: `apis` — APIs
- Children: 3
  - `funcdef-var` — var()
  - `typedef-var-args` — <var-args>
  - `replace-a-var-function` — replace a var() function

## Outgoing refs (13)

`webspec-index refs CSS-VARIABLES-1#using-variables -d outgoing -l 13`

## Incoming refs (1)

- CSS-VARIABLES-1#contents

### Possible effects

CSS-VARIABLES-1#using-variables

Partial analysis: additional effects may exist.

No effects detected by this analysis.

Traces and conditions (bounded): `webspec-index effects "CSS-VARIABLES-1#using-variables" --format markdown`
