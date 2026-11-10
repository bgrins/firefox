import JsonCodec

namespace CssDerivation.TypedCodec

def fixture : Lean.Json := json% {
  "schema": 1,
  "definitions": {
    "hexExpr": {
      "op": "or",
      "args": [
        {
          "op": "or",
          "args": [
            {
              "op": "and",
              "args": [
                {
                  "op": "leChar",
                  "args": [
                    {
                      "op": "scalar",
                      "args": [
                        48
                      ]
                    },
                    {
                      "op": "var",
                      "args": [
                        0
                      ]
                    }
                  ]
                },
                {
                  "op": "leChar",
                  "args": [
                    {
                      "op": "var",
                      "args": [
                        0
                      ]
                    },
                    {
                      "op": "scalar",
                      "args": [
                        57
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "op": "and",
              "args": [
                {
                  "op": "leChar",
                  "args": [
                    {
                      "op": "scalar",
                      "args": [
                        65
                      ]
                    },
                    {
                      "op": "var",
                      "args": [
                        0
                      ]
                    }
                  ]
                },
                {
                  "op": "leChar",
                  "args": [
                    {
                      "op": "var",
                      "args": [
                        0
                      ]
                    },
                    {
                      "op": "scalar",
                      "args": [
                        70
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        },
        {
          "op": "and",
          "args": [
            {
              "op": "leChar",
              "args": [
                {
                  "op": "scalar",
                  "args": [
                    97
                  ]
                },
                {
                  "op": "var",
                  "args": [
                    0
                  ]
                }
              ]
            },
            {
              "op": "leChar",
              "args": [
                {
                  "op": "var",
                  "args": [
                    0
                  ]
                },
                {
                  "op": "scalar",
                  "args": [
                    102
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    "whitespaceExpr": {
      "op": "or",
      "args": [
        {
          "op": "or",
          "args": [
            {
              "op": "eqChar",
              "args": [
                {
                  "op": "var",
                  "args": [
                    0
                  ]
                },
                {
                  "op": "scalar",
                  "args": [
                    10
                  ]
                }
              ]
            },
            {
              "op": "eqChar",
              "args": [
                {
                  "op": "var",
                  "args": [
                    0
                  ]
                },
                {
                  "op": "scalar",
                  "args": [
                    9
                  ]
                }
              ]
            }
          ]
        },
        {
          "op": "eqChar",
          "args": [
            {
              "op": "var",
              "args": [
                0
              ]
            },
            {
              "op": "scalar",
              "args": [
                32
              ]
            }
          ]
        }
      ]
    },
    "magnitudeExpr": {
      "op": "foldNat",
      "args": [
        {
          "op": "var",
          "args": [
            0
          ]
        },
        {
          "op": "nat",
          "args": [
            0
          ]
        },
        {
          "op": "add",
          "args": [
            {
              "op": "mul",
              "args": [
                {
                  "op": "var",
                  "args": [
                    1
                  ]
                },
                {
                  "op": "nat",
                  "args": [
                    16
                  ]
                }
              ]
            },
            {
              "op": "ite",
              "args": [
                {
                  "op": "leChar",
                  "args": [
                    {
                      "op": "var",
                      "args": [
                        0
                      ]
                    },
                    {
                      "op": "scalar",
                      "args": [
                        57
                      ]
                    }
                  ]
                },
                {
                  "op": "sub",
                  "args": [
                    {
                      "op": "code",
                      "args": [
                        {
                          "op": "var",
                          "args": [
                            0
                          ]
                        }
                      ]
                    },
                    {
                      "op": "nat",
                      "args": [
                        48
                      ]
                    }
                  ]
                },
                {
                  "op": "ite",
                  "args": [
                    {
                      "op": "leChar",
                      "args": [
                        {
                          "op": "var",
                          "args": [
                            0
                          ]
                        },
                        {
                          "op": "scalar",
                          "args": [
                            70
                          ]
                        }
                      ]
                    },
                    {
                      "op": "sub",
                      "args": [
                        {
                          "op": "code",
                          "args": [
                            {
                              "op": "var",
                              "args": [
                                0
                              ]
                            }
                          ]
                        },
                        {
                          "op": "nat",
                          "args": [
                            55
                          ]
                        }
                      ]
                    },
                    {
                      "op": "sub",
                      "args": [
                        {
                          "op": "code",
                          "args": [
                            {
                              "op": "var",
                              "args": [
                                0
                              ]
                            }
                          ]
                        },
                        {
                          "op": "nat",
                          "args": [
                            87
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            }
          ]
        }
      ]
    },
    "decodeExpr": {
      "op": "ite",
      "args": [
        {
          "op": "or",
          "args": [
            {
              "op": "or",
              "args": [
                {
                  "op": "eqNat",
                  "args": [
                    {
                      "op": "var",
                      "args": [
                        0
                      ]
                    },
                    {
                      "op": "nat",
                      "args": [
                        0
                      ]
                    }
                  ]
                },
                {
                  "op": "and",
                  "args": [
                    {
                      "op": "leNat",
                      "args": [
                        {
                          "op": "nat",
                          "args": [
                            55296
                          ]
                        },
                        {
                          "op": "var",
                          "args": [
                            0
                          ]
                        }
                      ]
                    },
                    {
                      "op": "leNat",
                      "args": [
                        {
                          "op": "var",
                          "args": [
                            0
                          ]
                        },
                        {
                          "op": "nat",
                          "args": [
                            57343
                          ]
                        }
                      ]
                    }
                  ]
                }
              ]
            },
            {
              "op": "ltNat",
              "args": [
                {
                  "op": "nat",
                  "args": [
                    1114111
                  ]
                },
                {
                  "op": "var",
                  "args": [
                    0
                  ]
                }
              ]
            }
          ]
        },
        {
          "op": "scalar",
          "args": [
            65533
          ]
        },
        {
          "op": "scalarOf",
          "args": [
            {
              "op": "var",
              "args": [
                0
              ]
            }
          ]
        }
      ]
    }
  },
  "program": {
    "op": "read",
    "args": [
      {
        "op": "raiseError",
        "args": [
          {
            "op": "ret",
            "args": [
              {
                "op": "scalar",
                "args": [
                  65533
                ]
              }
            ]
          }
        ]
      },
      {
        "op": "branch",
        "args": [
          {
            "op": "use",
            "args": [
              "hexExpr"
            ]
          },
          {
            "op": "scan",
            "args": [
              5,
              {
                "op": "use",
                "args": [
                  "hexExpr"
                ]
              },
              {
                "op": "scan",
                "args": [
                  1,
                  {
                    "op": "use",
                    "args": [
                      "whitespaceExpr"
                    ]
                  },
                  {
                    "op": "letE",
                    "args": [
                      {
                        "op": "cons",
                        "args": [
                          {
                            "op": "var",
                            "args": [
                              2
                            ]
                          },
                          {
                            "op": "var",
                            "args": [
                              1
                            ]
                          }
                        ]
                      },
                      {
                        "op": "letE",
                        "args": [
                          {
                            "op": "use",
                            "args": [
                              "magnitudeExpr"
                            ]
                          },
                          {
                            "op": "ret",
                            "args": [
                              {
                                "op": "use",
                                "args": [
                                  "decodeExpr"
                                ]
                              }
                            ]
                          }
                        ]
                      }
                    ]
                  }
                ]
              }
            ]
          },
          {
            "op": "ret",
            "args": [
              {
                "op": "var",
                "args": [
                  0
                ]
              }
            ]
          }
        ]
      }
    ]
  },
  "source_map": {
    "algorithm": {
      "anchor": "consume-escaped-code-point",
      "source_bytes": [
        48316,
        49501
      ]
    },
    "body": {
      "source_bytes": [
        48665,
        49501
      ],
      "operative_text": "Consume the next input code point. hex digit Consume as many hex digits as possible, but no more than 5. If the next input code point is whitespace, consume it as well. Interpret the hex digits as a hexadecimal number. If this number is zero, or is for a surrogate, or is greater than the maximum allowed code point, return U+FFFD REPLACEMENT CHARACTER (\ufffd). Otherwise, return the code point with that value. EOF This is a parse error. Return U+FFFD REPLACEMENT CHARACTER (\ufffd). anything else Return the current input code point."
    },
    "definitions": {
      "digit": {
        "text": "A code point between U+0030 DIGIT ZERO (0) and U+0039 DIGIT NINE (9) inclusive.",
        "source_bytes": [
          29293,
          29462
        ]
      },
      "hex digit": {
        "text": "A digit, or a code point between U+0041 LATIN CAPITAL LETTER A (A) and U+0046 LATIN CAPITAL LETTER F (F) inclusive, or a code point between U+0061 LATIN SMALL LETTER A (a) and U+0066 LATIN SMALL LETTER F (f) inclusive.",
        "source_bytes": [
          29466,
          29753
        ]
      },
      "newline": {
        "text": "U+000A LINE FEED.",
        "source_bytes": [
          33496,
          33785
        ]
      },
      "whitespace": {
        "text": "A newline, U+0009 CHARACTER TABULATION, or U+0020 SPACE.",
        "source_bytes": [
          33789,
          33930
        ]
      },
      "maximum allowed code point": {
        "text": "The greatest code point defined by Unicode: U+10FFFF.",
        "source_bytes": [
          33934,
          34049
        ]
      },
      "leading surrogate": {
        "text": "A leading surrogate is a code point that is in the range U+D800 to U+DBFF, inclusive.",
        "source": "infra",
        "source_bytes": [
          42391,
          42504
        ]
      },
      "trailing surrogate": {
        "text": "A trailing surrogate is a code point that is in the range U+DC00 to U+DFFF, inclusive.",
        "source": "infra",
        "source_bytes": [
          42506,
          42620
        ]
      },
      "surrogate": {
        "text": "A surrogate is a leading surrogate or a trailing surrogate.",
        "source": "infra",
        "source_bytes": [
          42622,
          42716
        ]
      }
    },
    "roles": {
      "read": "Initial next-input consumption and EOF/literal dispatch",
      "first scan": "Maximal bounded additional hex consumption",
      "second scan": "Conditional single whitespace terminator",
      "first local": "Assemble first consumed scalar plus additional hex digits",
      "second local": "Interpret the hex digits as a hexadecimal number",
      "decodeExpr": "Zero/surrogate/maximum replacement or scalar result"
    }
  }
}

end CssDerivation.TypedCodec
