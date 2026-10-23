    case StyleDisplayInside::Table: {
      static constexpr FrameConstructionData data(
          &nsCSSFrameConstructor::ConstructTable);
      return &data;
    }
