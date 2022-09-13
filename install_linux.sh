echo "------------------------------------------"
echo " _   _      _   ____   ___  ____  "
echo "| \ | | ___| |_|  _ \ / _ \/ ___| "
echo "|  \| |/ _ \ __| |_) | | | \___ \ "
echo "| |\  |  __/ |_|  __/| |_| |___) |"
echo "|_| \_|\___|\__|_|    \___/|____/ "
echo ""
echo "              v1.1 by Nick Tonjum "
echo ""
echo ""
if [ `whoami` != root ]; then
    echo Please run this script as root or using sudo
    echo ""
    echo Installation failed.
    echo "------------------------------------------"
    exit
fi
echo "Installing..."
echo ""
apt-get update
apt-get --yes install onboard
apt-get --yes install python3-tk
apt-get --yes install python3-pil.imagetk
pip3 install pymongo
pip3 install tkcolorpicker
pip3 install webcolors 
echo ""
echo "Install Complete!"
echo ""
echo "------------------------------------------"
