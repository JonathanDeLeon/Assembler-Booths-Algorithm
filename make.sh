python assembler.py
while true; do
    read -p "Do you wish to compute machine instructions?" yn
    case $yn in
        [Yy]* ) python algorithm.py; break;;
        [Nn]* ) exit;;
        * ) echo "Please answer yes or no.";;
    esac
done
