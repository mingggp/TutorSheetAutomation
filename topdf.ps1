# แปลง .docx เป็น .pdf ด้วย Microsoft Word ที่ติดตั้งอยู่ในเครื่อง
#
# ใช้ Word แทนการเขียนตัววาด PDF ตัวที่สอง เพราะสไตล์จะไม่มีทางเพี้ยนจากชีทจริง
# เครื่องนี้ไม่มี LibreOffice แต่มี Word อยู่แล้ว
#
#   powershell -ExecutionPolicy Bypass -File topdf.ps1 "out\a.docx" "out\b.docx"
#   powershell -ExecutionPolicy Bypass -File topdf.ps1 "out\*.docx"
#
# **ระวัง** ชื่อไฟล์ของเรามีวงเล็บเหลี่ยมอย่าง "[TPAT3] Medium.docx"
# ซึ่ง PowerShell ตีความ [ ] เป็น wildcard (ชุดตัวอักษร) ไม่ใช่ตัวอักษรธรรมดา
# จึงต้องใช้ -LiteralPath กับชื่อที่ไม่มี * หรือ ? เท่านั้น ไม่งั้นจะหาไฟล์ไม่เจอ

param([Parameter(ValueFromRemainingArguments = $true)][string[]]$Files)

if (-not $Files) { Write-Output "ใช้: topdf.ps1 <ไฟล์.docx> [...]"; exit 1 }

$paths = @()
foreach ($f in $Files) {
  if ($f -match '[*?]') {
    # มี wildcard จริง -> ให้ PowerShell ขยายให้
    $items = Get-ChildItem -Path $f -File -ErrorAction SilentlyContinue
  } else {
    # ชื่อตรงตัว -> LiteralPath เท่านั้น กันวงเล็บเหลี่ยมถูกตีความเป็น wildcard
    $items = Get-Item -LiteralPath $f -ErrorAction SilentlyContinue
  }
  if (-not $items) { Write-Output "ไม่เจอไฟล์: $f"; continue }
  foreach ($it in $items) { if ($it.FullName -like "*.docx") { $paths += $it.FullName } }
}
if (-not $paths) { Write-Output "ไม่มีไฟล์ .docx ให้แปลง"; exit 1 }

try {
  $word = New-Object -ComObject Word.Application
} catch {
  Write-Output "เปิด Word ไม่ได้ - ต้องมี Microsoft Word ติดตั้งอยู่"
  exit 1
}
$word.Visible = $false
$word.DisplayAlerts = 0

$ok = 0
foreach ($src in $paths) {
  $dst = [System.IO.Path]::ChangeExtension($src, ".pdf")
  try {
    # ReadOnly=true กันไม่ให้ Word ไปแก้ไฟล์ต้นทาง
    $doc = $word.Documents.Open($src, $false, $true)
    $doc.SaveAs([ref]$dst, [ref]17)      # 17 = wdFormatPDF
    $doc.Close($false)
    $size = [math]::Round((Get-Item -LiteralPath $dst).Length / 1KB)
    Write-Output ("OK   {0}  ({1} KB)" -f [System.IO.Path]::GetFileName($dst), $size)
    $ok++
  } catch {
    Write-Output ("พัง  {0}  -  {1}" -f [System.IO.Path]::GetFileName($src), $_.Exception.Message)
  }
}

$word.Quit()
[void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($word)
Write-Output "แปลงสำเร็จ $ok จาก $($paths.Count) ไฟล์"
