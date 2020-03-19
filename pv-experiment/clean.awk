#!/usr/bin/env nix-shell
#!nix-shell -i "gawk -f" -p gawk

BEGIN {
  FS = "\t"
  OFS = "\t"
}

NR == 1 {
  for (i = 1; i <= NF; ++i)
    first[i] = $i
}

NR == 2 {
  line = ""
  for (i = 1; i <= NF; ++i) {
    if (i > 1)
      line = line OFS
    line = line first[i] " | " $i
  }
  print line
}

NR >= 3 {
  print
}
