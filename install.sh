echo "------------------------------------------"
echo " _   _      _   ____   ___  ____  "
echo "| \ | | ___| |_|  _ \ / _ \/ ___| "
echo "|  \| |/ _ \ __| |_) | | | \___ \ "
echo "| |\  |  __/ |_|  __/| |_| |___) |"
echo "|_| \_|\___|\__|_|    \___/|____/ "
echo ""
echo "              v1.0 by Nick Tonjum "
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
apt-get -qq update
apt-get -qq --yes install onboard
echo ""
echo "Install Complete!"
echo ""
echo "------------------------------------------"
