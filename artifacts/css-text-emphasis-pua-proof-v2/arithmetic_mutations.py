ARITHMETIC_MUTATIONS = {
    "floor_negative": ("int64_t(ligatureWidth) / totalClusterCount", "(int64_t(ligatureWidth) - (ligatureWidth < 0 ? int64_t(totalClusterCount)-1 : 0)) / totalClusterCount"),
    "narrow_denominator": ("int64_t(ligatureWidth) / totalClusterCount", "int64_t(ligatureWidth) / int32_t(totalClusterCount)"),
    "unsigned_quotient": ("int64_t(ligatureWidth) / totalClusterCount", "uint32_t(ligatureWidth) / totalClusterCount"),
    "omit_remainder": ("result.mPartWidth += ligatureWidth - allParts;", "result.mPartWidth += 0;"),
    "omit_part_index": ("result.mPartAdvance = partClusterIndex * advancePerCluster;", "result.mPartAdvance = 0;"),
}
