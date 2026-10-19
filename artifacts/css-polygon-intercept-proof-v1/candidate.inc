nscoord nsFloatManager::PolygonShapeInfo::XInterceptAtY(const nscoord aY,
                                                        const nsPoint& aP1,
                                                        const nsPoint& aP2) {
  // Solve for x in the linear equation: x = x1 + (y-y1) * (x2-x1) / (y2-y1),
  // where aP1 = (x1, y1) and aP2 = (x2, y2).

  MOZ_ASSERT(aP1.y <= aY && aY <= aP2.y,
             "This function won't work if the horizontal line at aY and "
             "the line segment (aP1, aP2) do not intersect!");

  MOZ_ASSERT(aP1.y != aP2.y,
             "A horizontal line segment results in dividing by zero error!");

  return aP1.x + NSCoordMulDiv(aY - aP1.y, aP2.x - aP1.x, aP2.y - aP1.y);
}
