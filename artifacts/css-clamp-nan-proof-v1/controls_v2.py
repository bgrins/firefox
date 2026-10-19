MUTATIONS = {
    'WrongLowerWinner': ('Candidate.lean', 'if ab == .gt then some a else', 'if ab == .gt then some b else'),
    'WrongUpperWinner': ('Candidate.lean', 'if ca == .lt then some a else some c', 'if ca == .lt then some c else some c'),
    'WrongCenterWinner': ('Candidate.lean', '      else some b\n\ntheorem winner_sound', '      else some c\n\ntheorem winner_sound'),
    'DropUnknownChild': ('Candidate.lean', '| _, _, _ => .clamp a b c\n\ntheorem fold_sound', '| _, _, _ => a\n\ntheorem fold_sound'),
    'DropPercentageGuard': ('Candidate.lean', '| some _ => api.hint leaf != .unresolvedPercentage', '| some _ => true'),
    'DropRelativeResultGuard': ('Candidate.lean', '| some value => !finiteNumber value\n  else true', '| some _ => true\n  else true'),
    'DropFallbackNaN': ('Candidate.lean', 'api.nanTest c == some false then winner api a b c else none', 'true then winner api a b c else none'),
    'UnsafeZeroBasisFold': ('Scaling.lean', '!(hasInfinity a || hasInfinity b || hasInfinity c) || !finiteNumber (specClamp a b c)', 'true'),
}
MODULES = ['Clamp.lean', 'Scaling.lean', 'Candidate.lean', 'Instances.lean']
