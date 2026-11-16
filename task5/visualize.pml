load alignment/aligned_esmfold.pdb, esmfold
load alignment/aligned_rosettafold2.pdb, rosettafold2
alter rosettafold2, chain='B'
sort
hide everything
show cartoon
color cyan, chain A
color orange, chain B
set bg_rgb, [1, 1, 1]
set ray_opaque_background, 1
set ray_shadows, 0
set antialias, 2
set cartoon_fancy_helices, 1
orient
zoom all, 0
save alignment/alignment.pse
png alignment/alignment.png, width=1800, height=900, dpi=300, ray=1
rotate y, 90
png alignment/alignment_rotated.png, width=1000, height=1200, dpi=300, ray=1
