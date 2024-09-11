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
    echo -e "${RED}      
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
    echo -e "${YELLOW}5.${NC} Check system info"
    echo -e "${YELLOW}6.${NC} View logs"
    echo -e "${YELLOW}7.${NC} Backup files"
    echo -e "${YELLOW}8.${NC} Manage files"
    echo -e "${YELLOW}9.${NC} Show battery status"
    echo -e "${YELLOW}10.${NC} List running processes"
    echo -e "${YELLOW}11.${NC} Custom command"
    echo -e "${YELLOW}12.${NC} Check network status"
    echo -e "${YELLOW}13.${NC} Run a security scan"
    echo -e "${YELLOW}14.${NC} Display system information"
    echo -e "${YELLOW}15.${NC} Schedule a task"
    echo -e "${YELLOW}16.${NC} Manage user accounts"
    echo -e "${YELLOW}17.${NC} Showing network interface"
    echo -e "${YELLOW}18.${NC} Exit"
    echo -e "${CYAN}=============================${NC}"
}

function update_packages() {
    echo -e "${GREEN}Updating packages...${NC}"
    pkg update && pkg upgrade
    read -p "Press enter to continue..."
}

# Function for installing a package
function install_package() {
    read -p "Enter the name of the package to install: " package
    echo -e "${GREEN}Installing $package...${NC}"
    pkg install $package
    read -p "Press enter to continue..."
}

# Function for clearing storage
function clear_storage() {
    echo -e "${RED}Clearing storage...${NC}"
    termux-setup-storage
    rm -rf /data/data/com.termux/files/home/storage/*
    read -p "Press enter to continue..."
}

# Function for showing disk usage
function show_disk_usage() {
    echo -e "${CYAN}Showing disk usage...${NC}"
    df -h
    read -p "Press enter to continue..."
}

# Function for checking system info
function check_system_info() {
    echo -e "${GREEN}Checking system info...${NC}"
    uname -a
    read -p "Press enter to continue..."
}

# Function for viewing logs
function view_logs() {
    echo -e "${CYAN}Viewing logs...${NC}"
    logcat -d | less
    read -p "Press enter to continue..."
}

# Function for backing up files
function backup_files() {
    echo -e "${YELLOW}Backing up files...${NC}"
    read -p "Enter backup destination directory: " backup_dir
    mkdir -p "$backup_dir"
    cp -r /data/data/com.termux/files/home/* "$backup_dir"
    echo -e "${GREEN}Backup completed to $backup_dir${NC}"
    read -p "Press enter to continue..."
}

# Function for managing files
function manage_files() {
    echo -e "${CYAN}Managing files...${NC}"
    read -p "Enter directory to manage: " dir
    ls -al "$dir"
    read -p "Press enter to continue..."
}

# Function for showing battery status
function show_battery_status() {
    echo -e "${GREEN}Showing battery status...${NC}"
    termux-battery-status
    read -p "Press enter to continue..."
}

# Function for listing running processes
function list_running_processes() {
    echo -e "${CYAN}Listing running processes...${NC}"
    ps aux
    read -p "Press enter to continue..."
}

# Function for executing a custom command
function custom_command() {
    echo -e "${YELLOW}Executing custom command...${NC}"
    read -p "Enter your command: " cmd
    eval $cmd
    read -p "Press enter to continue..."
}

# Function for checking network status
function check_network_status() {
    echo -e "${CYAN}Checking network status...${NC}"
    ifconfig
    read -p "Press enter to continue..."
}

# Function for running a security scan
function run_security_scan() {
    echo -e "${RED}Running security scan...${NC}"
    pkg install lynis -y
    lynis audit system
    read -p "Press enter to continue..."
}

function display_system_info() {
    echo -e "${GREEN}Displaying system information...${NC}"
    lscpu
    free -h
    top -n 1
    read -p "Press enter to continue..."
}

# Function for scheduling a task
function schedule_task() {
    echo -e "${YELLOW}Scheduling a task...${NC}"
    read -p "Enter the task command: " task_cmd
    read -p "Enter the time (e.g., 'now + 1 hour'): " task_time
    echo "$task_cmd" | at "$task_time"
    echo -e "${GREEN}Task scheduled.${NC}"
    read -p "Press enter to continue..."
}

# Function for managing user accounts
function manage_user_accounts() {
    echo -e "${CYAN}Managing user accounts...${NC}"
    read -p "Enter username to add: " username
    useradd $username
    echo -e "${GREEN}User $username added.${NC}"
    read -p "Press enter to continue..."
}

function show_network_interfaces() {
    echo -e "${CYAN}Showing network interfaces...${NC}"
    ip link show
    read -p "Press enter to continue..."
}

while true
do
    show_menu
    read -p "Choose an option [1-17]: " choice
    case $choice in
        1) update_packages ;;
        2) install_package ;;
        3) clear_storage ;;
        4) show_disk_usage ;;
        5) check_system_info ;;
        6) view_logs ;;
        7) backup_files ;;
        8) manage_files ;;
        9) show_battery_status ;;
        10) list_running_processes ;;
        11) custom_command ;;
        12) check_network_status ;;
        13) run_security_scan ;;
        14) display_system_info ;;
        15) schedule_task ;;
        16) manage_user_accounts ;;
        17) echo -e "${GREEN}Goodbye!${NC}"; exit ;;
        *) echo -e "${RED}Invalid choice!${NC}" ;;
    esac
done
