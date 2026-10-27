bool SVGLength::IsAbsoluteUnit(uint16_t aUnit) {
  return aUnit == SVG_LENGTHTYPE_NUMBER ||
         (aUnit >= SVG_LENGTHTYPE_PX && aUnit <= SVG_LENGTHTYPE_Q);
}

float SVGLength::GetAbsUnitsPerAbsUnit(uint16_t aUnits, uint16_t aPerUnit) {
  MOZ_ASSERT(SVGLength::IsAbsoluteUnit(aUnits), "Not a CSS absolute unit");
  MOZ_ASSERT(SVGLength::IsAbsoluteUnit(aPerUnit), "Not a CSS absolute unit");

  static const float CSSAbsoluteUnitConversionFactors[7][7] = {
      // columns: px, cm, mm, in, pt, pc, q
      // px per...:
      {1.0f, 37.7952755906f, 3.779528f, 96.0f, 1.33333333333333333f, 16.0f,
       0.94488188988f},
      // cm per...:
      {0.02645833333f, 1.0f, 0.1f, 2.54f, 0.035277777777777778f,
       0.42333333333333333f, 0.025f},
      // mm per...:
      {0.26458333333f, 10.0f, 1.0f, 25.4f, 0.35277777777777778f,
       4.2333333333333333f, 0.25f},
      // in per...:
      {0.01041666666f, 0.39370078740157481f, 0.039370078740157481f, 1.0f,
       0.013888888888888889f, 0.16666666666666667f, 0.02204860853f},
      // pt per...:
      {0.75f, 28.346456692913386f, 2.8346456692913386f, 72.0f, 1.0f, 12.0f,
       0.70866141732f},
      // pc per...:
      {0.0625f, 2.3622047244094489f, 0.23622047244094489f, 6.0f,
       0.083333333333333333f, 1.0f, 16.9333333333f},
      // q per...:
      {1.0583333332f, 40.0f, 4.0f, 45.354336f, 1.41111111111f, 16.9333333333f,
       1.0f}};

  auto ToIndex = [](uint16_t aUnit) {
    return aUnit == SVG_LENGTHTYPE_NUMBER ? 0 : aUnit - 5;
  };

  return CSSAbsoluteUnitConversionFactors[ToIndex(aUnits)][ToIndex(aPerUnit)];
}
