echo "Trying to rename impact file patch folder to a consistent & short name..."
for /D %%f in (C:\Users\op_2150\Desktop\ImpactFiles\*) do rename "%%f" "patch"
echo "We have successfully renamed the patch folder"