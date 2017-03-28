$xml = [xml](Get-Content .\start.xml)
$ScriptsPath = $xml.PATH_CONFIG.Scripts
$ProjectPath = $xml.PATH_CONFIG.MyProject
cd $ScriptsPath 
.\activate.ps1
cd $ProjectPath 
scrapy crawlall
cd $ScriptsPath 
.\deactivate
exit






