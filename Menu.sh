#!/bin/bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Function to display the menu
function show_menu() {
    clear
    echo -e "${CYAN}=============================${NC}"
    echo -e "${GREEN}      
██╗  ██╗ ██████╗ ███████╗ ██████╗██╗   ██╗██╗███╗   ██╗████████╗
██║  ██║██╔═══██╗╚══███╔╝██╔════╝╚██╗ ██╔╝██║████╗  ██║╚══██╔══╝
███████║██║   ██║  ███╔╝ ██║      ╚████╔╝ ██║██╔██╗ ██║   ██║   
╚════██║██║   ██║ ███╔╝  ██║       ╚██╔╝  ██║██║╚██╗██║   ██║   
     ██║╚██████╔╝███████╗╚██████╗   ██║██╗██║██║ ╚████║   ██║   
     ╚═╝ ╚═════╝ ╚══════╝ ╚═════╝   ╚═╝╚═╝╚═╝╚═╝  ╚═══╝   ╚═╝${NC}"
    echo -e "${CYAN}=============================${NC}"
    echo -e "${YELLOW}1.${NC} Update packages"
    echo -e "${YELLOW}2.${NC} Install a package"
    echo -e "${YELLOW}3.${NC} Clear storage"
    echo -e "${YELLOW}4.${NC} Show disk usage"
    echo -e "${YELLOW}5.${NC} Exit"
    echo -e "${CYAN}=============================${NC}"
}

function menu() {
    clear
    display_banner
    echo -e "${CYAN}1. View Network Connections${NC}"
    echo -e "${CYAN}2. Check System Load${NC}"
    echo -e "${CYAN}3. Show Disk I/O Statistics${NC}"
    echo -e "${CYAN}4. Check Memory Usage${NC}"
    echo -e "${CYAN}5. Show System Logs${NC}"
    echo -e "${CYAN}6. Manage Installed Packages${NC}"
    echo -e "${CYAN}7. Show Active Users${NC}"
    echo -e "${CYAN}8. Restart Termux${NC}"
    echo -e "${CYAN}9. Show Scheduled Tasks${NC}"
    echo -e "${CYAN}10. Cancel a Scheduled Task${NC}"
    echo -e "${CYAN}11. List Available Updates${NC}"
    echo -e "${CYAN}12. Display System Date and Time${NC}"
    echo -e "${CYAN}13. Check Uptime${NC}"
    echo -e "${CYAN}14. Display System Temperature${NC}"
    echo -e "${CYAN}15. Show Network Interfaces${NC}"
    echo -e "${CYAN}16. Change Directory${NC}"
    echo -e "${CYAN}17. View File Contents${NC}"
    echo -e "${CYAN}18. Edit a File${NC}"
    echo -e "${CYAN}19. Create a Directory${NC}"
    echo -e "${CYAN}20. Delete a Directory${NC}"
    echo -e "${CYAN}21. Create a File${NC}"
    echo -e "${CYAN}22. Delete a File${NC}"
    echo -e "${CYAN}23. Check for Disk Errors${NC}"
    echo -e "${CYAN}24. Show Last Login Information${NC}"
    echo -e "${CYAN}25. Monitor System Performance${NC}"
    echo -e "${CYAN}26. Check for Available Disk Space${NC}"
    echo -e "${CYAN}27. View System Processes${NC}"
    echo -e "${CYAN}28. List Open Files${NC}"
    echo -e "${CYAN}29. View Network Statistics${NC}"
    echo -e "${CYAN}30. Show Kernel Version${NC}"
    echo -e "${CYAN}31. List Services${NC}"
    echo -e "${CYAN}32. Check Battery Health${NC}"
    echo -e "${CYAN}33. Backup System Configuration${NC}"
    echo -e "${CYAN}34. Restore System Configuration${NC}"
    echo -e "${CYAN}35. Network Troubleshooting${NC}"
    echo -e "${CYAN}36. Monitor Disk Usage${NC}"
    echo -e "${CYAN}37. Check System Integrity${NC}"
    echo -e "${CYAN}38. View Package Version${NC}"
    echo -e "${CYAN}39. Scan for Malware${NC}"
    echo -e "${CYAN}40. Show User Groups${NC}"
    echo -e "${CYAN}41. Manage Startup Applications${NC}"
    echo -e "${CYAN}42. Check System Security${NC}"
    echo -e "${CYAN}43. Display System Environment Variables${NC}"
    echo -e "${CYAN}44. List Available Commands${NC}"
    echo -e "${CYAN}45. View System Configuration Files${NC}"
    echo -e "${CYAN}46. Manage System Users${NC}"
    echo -e "${CYAN}47. View Running Services${NC}"
    echo -e "${CYAN}48. Show Process Statistics${NC}"
    echo -e "${CYAN}49. System Health Check${NC}"
    echo -e "${CYAN}50. Exit${NC}"
}

function handle_choice() {
    local choice
    read -p "Enter your choice: " choice

    case $choice in
        1) netstat -tuln ;;
        2) uptime ;;
        3) iostat ;;
        4) free -h ;;
        5) dmesg | less ;;
        6) pkg list-installed ;;
        7) who ;;
        8) termux-reload-settings ;;
        9) atq ;;
        10) atrm ;;
        11) apt update ;;
        12) date ;;
        13) uptime ;;
        14) cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000 "°C"}' ;;
        15) ifconfig ;;
        16) cd ;;
        17) cat ;;
        18) nano ;;
        19) mkdir ;;
        20) rmdir ;;
        21) touch ;;
        22) rm ;;
        23) fsck ;;
        24) last ;;
        25) top ;;
        26) df -h ;;
        27) ps aux ;;
        28) lsof ;;
        29) ss ;;
        30) uname -r ;;
        31) service --status-all ;;
        32) termux-battery-status ;;
        33) cp -r /data/data/com.termux/files/home /data/data/com.termux/files/home_backup ;;
        34) cp -r /data/data/com.termux/files/home_backup /data/data/com.termux/files/home ;;
        35) ping google.com ;;
        36) du -sh ;;
        37) debsums ;;
        38) apt list --installed ;;
        39) clamscan ;;
        40) groups ;;
        41) termux-wake-lock ;;
        42) lynis audit system ;;
        43) printenv ;;
        44) compgen -c ;;
        45) ls /etc ;;
        46) usermod ;;
        47) systemctl status ;;
        48) ps auxf ;;
        49) top ;;
        50) exit 0 ;;
        *) echo -e "${RED}Invalid choice. Please try again.${NC}" ;;
    esac
}

# Main Loop
while true; do
    menu
    handle_choice
done
