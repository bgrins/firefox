MUTATIONS = {
    'OldEarlyReturn': ('missing convertedMask channel || missing sourceMask channel', 'missing convertedMask channel'),
    'OverwriteConverted': ('missing convertedMask channel || missing sourceMask channel', 'missing sourceMask channel'),
    'RedOnly': ('missing convertedMask channel || missing sourceMask channel', 'missing convertedMask channel || (channel.val == 0 && missing sourceMask channel)'),
    'WrongCopyDirection': ('| true, false => .useRight', '| true, false => .useLeft'),
}
