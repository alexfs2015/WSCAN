from os import system, name, path
import whois
import socket
from time import sleep
from usp.tree import sitemap_tree_for_homepage
from colorama import init, Fore, Style
from pyfiglet import Figlet
import requests

def clear():
    if name == "nt":
        _ = system('cls')
    else:
        _ = system('clear')

def main():
    clear()
    f = Figlet(font='slant')
    print(Fore.YELLOW + f.renderText('WSCAN') + Style.RESET_ALL)
    
    choice = main_menu()
    if choice == 1:
        get_information()
    elif choice == 2:
        get_ip()
    elif choice == 3:
        get_sitemap()
    elif choice == 4:
        get_tech()
    elif choice == 5:
        exit()

def main_menu():
    options = (Fore.CYAN +'1. Information of domain\n'
                '2. Get IP from domain\n'
                '3. Get sitemap from url\n'
                '4. Check website CMS\n'
                '5. Exit' + Style.RESET_ALL +
                '\n\nEnter a number: ' )
    choice = input(options)
    try:
        return(int(choice))
    except:
        clear()
        print(Fore.RED + "[!] Please enter a valid number!" + Style.RESET_ALL)
        sleep(3)
        main()
    
def request(url):
    global user_agent
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
    }
    return(requests.get(url, allow_redirects=False, headers=user_agent))


#OPTION 1
def get_information():
    clear()
    url = input("Enter the domain of website: ")
    domain = whois.whois(url)

    if(domain['domain_name'] == None and domain['registrar'] == None and domain['whois_server'] == None):
        clear()
        print(Fore.RED + "[!] Please enter a valid domain!" + Style.RESET_ALL)
        sleep(3)
        get_information()

#OPTION 2
def get_ip():
    clear()
    website = (input("Enter the domain of website: "))
    try:
        print("[+] The IP of domain is: " + socket.gethostbyname(website))
    except:
        clear()
        print(Fore.RED + "[!] Please enter a valid domain!" + Style.RESET_ALL)
        sleep(3)
        get_ip()

#OPTION 3
def get_sitemap():
    clear()
    url = input("Enter the website url: ")
    try:
        tree = sitemap_tree_for_homepage(url)
    except:
        clear()
        print(Fore.RED + "[!] Please enter a valid url!" + Style.RESET_ALL)
        sleep(3)
        get_sitemap()
    clear()
    print('Sitemap of ' + '"' + url + '":')
    for page in tree.all_pages():
        print(page)

#OPTION 4
def get_tech():
    clear()
    url = input("Enter the website url: ")

    #Check the input for HTTP or HTTPS and then remove it, if nothing is found assume HTTP
    if(url.startswith("http://")):
        proto = "http://"
        url = url[7:]
        print(url)
    elif(url.startswith("https://")):
        proto = "https://"
        url = url[8:]
    else:
        proto = "http://"
    
    #Check the input for an ending / and remove it if found
    if(url.endswith("/")):
        url = url.strip("/")

    #Combine protocol and website
    url = proto + url

    #Check if site is online
    print("[+] Checking if site is online...")

    try:
        online_check = request(url)
    except requests.exceptions.ConnectionError as ex:
        print("[!] " + url + " appears to be offline.")
    else:
        if(online_check.status_code == 200 or online_check.status_code == 301 or online_check.status_code == 302):
            print(" |  " + url + " appears to be online.")
            print("\nScanning...")
            print("[+] Checking if the site is redirecting")
            redirect_check = requests.get(url, headers=user_agent)
            if(len(redirect_check.history) > 0):
                if('301' in str(redirect_check.history[0]) or '302' in str(redirect_check.history[0])):
                    print("[!] It appears the site is redirecting to " + redirect_check.url)
            elif('meta http-equiv="REFRESH"' in redirect_check.text):
                print("[!] The site appears to be redirecting!")
            else:
                print(" | Site does not appear to be redirecting...")
        else:
            print("[!] " + url + "appears to be online but returned a " + str(online_check.status_code) + " error.\n")
            exit()

        print("\n[+] Attempting to get the HTTP headers...")
        for header in online_check.headers:
            try:
                print(" |  " + header + " : " + online_check.headers[header])
            except Exception as ex:
                print("[!] Error: " + ex.message)

        ####################################################
        # WordPress Scans
        ####################################################

        print("\n[+] Running the WordPress scans...")

        wp_login_check = requests.get(url + "/wp-login.php", headers=user_agent)
        if(wp_login_check.status_code == 200 and "user_login" in wp_login_check.text and "404" not in wp_login_check.text):
            print(Fore.YELLOW + "[!] Detected: WordPress WP-Login page: " + url + "/wp-login.php" + Style.RESET_ALL) 
        else:
            print(" |  Not Detected: WordPress WP-Login page: " + url + "/wp-login.php")

        wp_admin_check = requests.get(url + "/wp-admin", headers=user_agent)
        if(wp_admin_check.status_code == 200 and "user_login" in wp_admin_check.text and "404" not in wp_login_check.text):
            print(Fore.YELLOW + "[!] Detected: WordPress WP-Admin page: " + url + '/wp-admin' + Style.RESET_ALL)
        else:
            print(" |  Not Detected: WordPress WP-Admin page: " + url + '/wp-admin')

        wp_admin_upgrade_check = request(url + "/wp-admin/upgrade.php")
        if(wp_admin_upgrade_check.status_code == 200 and "404" not in wp_admin_upgrade_check.text):
            print(Fore.YELLOW + "[!] Detected: WordPress WP-Admin/upgrade.php page: " + url + '/wp-admin/upgrade.php' + Style.RESET_ALL)
        else:
            print(" |  Not Detected: WordPress WP-Admin/upgrade.php page: " + url + '/wp-admin/upgrade.php')

        wp_admin_readme_check = request(url + "/readme.html")
        if(wp_admin_readme_check.status_code == 200 and "404" not in wp_admin_readme_check.text):
            print(Fore.YELLOW + "[!] Detected: WordPress Readme.html: " + url + '/readme.html' + Style.RESET_ALL)
        else:
            print(" |  Not Detected: WordPress Readme.html: " + url + '/readme.html')

        wp_links_check = request(url)
        if("wp-" in wp_links_check.text):
            print(Fore.YELLOW + "[!] Detected: WordPress wp- style links detected on index" + Style.RESET_ALL)
        else:
            print(" |  Not Detected: WordPress wp- style links detected on index")

        ####################################################
        # Joomla Scans
        ####################################################

        print("\n[+] Running the Joomla scans...")

        joomla_admin_check = request(url + "/administrator/")
        if(joomla_admin_check.status_code == 200 and "mod-login-username" in joomla_admin_check.text and "404" not in joomla_admin_check.text):
            print(Fore.YELLOW + "[!] Detected: Potential Joomla administrator login page: " + url + '/administrator/' + Style.RESET_ALL)
        else:
            print(" |  Not Detected: Joomla administrator login page: " + url + '/administrator/')
        
        joomla_readme_check = request(url + "/readme.txt")
        if(joomla_readme_check.status_code == 200 and "joomla" in joomla_readme_check.text and "404" not in joomla_readme_check):
            print(Fore.YELLOW + "[!] Detected: Joomla Readme.txt: " + url + '/readme.txt' + Style.RESET_ALL)
        else:
            print(" |  Not Detected: Joomla Readme.txt: " + url + '/readme.txt')
        
        joomla_tag_check = request(url)
        if(joomla_tag_check.status_code == 200 and 'name="generator" content="Joomla' in joomla_tag_check.text and "404" not in joomla_tag_check.text):
            print(Fore.YELLOW + "[!] Detected: Generated by Joomla tag on index" + Style.RESET_ALL)
        else:
            print(" |  Not Detected: Generated by Joomla tag on index")
        
        joomla_string_check = request(url)
        if(joomla_string_check.status_code == 200 and "joomla" in joomla_string_check.text and "404" not in joomla_string_check.text):
            print(Fore.YELLOW + "[!] Detected: Joomla strings on index" + Style.RESET_ALL)
        else:
            print(" |  Not Detected: Joomla strings on index")
        
        joomla_dir_check = request(url + '/media/com_joomlaupdate/')
        if(joomla_dir_check.status_code == 403 and "404" not in joomla_dir_check.text):
            print(Fore.YELLOW + "[!] Detected: Joomla media/com_joomlaupdate directories: " + url + '/media/com_joomlaupdate/' + Style.RESET_ALL)
        else:
            print(" |  Not Detected: Joomla media/com_joomlaupdate directories: " + url + '/media/com_joomlaupdate/')


if __name__ == "__main__":
    init()
    main()
