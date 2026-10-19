if (colSpan > 1) {
            // If a column-spanning cell is in the first row, split up
            // the space evenly.  (XXX This isn't quite right if some of
            // the columns it's in have specified inline sizes.  Should
            // we care?)
            cellISize =
                std::max(0, ((cellISize + spacing) / colSpan) - spacing);
          }
