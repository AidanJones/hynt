export const BP_EPOCH = 1950;
export const ordinal = year => year < 0 ? year + 1 : year;
export const civil = value => value <= 0 ? value - 1 : value;
export const bpToCivil = bp => civil(BP_EPOCH - bp);
export const civilToBP = year => BP_EPOCH - ordinal(year);
