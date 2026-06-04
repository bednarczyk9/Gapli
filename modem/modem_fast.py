import requests
from huawei_lte_api.Connection import Connection
from huawei_lte_api.Client import Client
import time

def get_public_ip():
    try:
        response = requests.get('https://api.ipify.org', timeout=10)
        return response.text.strip()
    except Exception:
        return None

def reset_modem_ip(url='http://admin:niusia6@192.168.8.1/'):
    print("Getting current IP...")
    ip_before = get_public_ip()
    print(f"Current IP: {ip_before}")
    
    start_time = time.time()
    
    try:
        with Connection(url) as connection:
            client = Client(connection)
            
            # Get current PLMN and RAT to be accurate
            print("Detecting network settings...")
            plmn_info = client.net.current_plmn()
            plmn = plmn_info.get('Numeric')
            rat = plmn_info.get('Rat')
            
            if not plmn:
                print("Could not detect PLMN, using default 26002 (T-Mobile PL)")
                plmn = '26002'
            if not rat:
                rat = '7' # LTE
                
            print(f"Force re-registering on network (PLMN: {plmn}, RAT: {rat})...")
            # Switch to Manual to force disconnect
            client.net.set_register('1', plmn, rat)
            
            # Switch back to Auto to reconnect
            client.net.set_register('0', plmn, rat)
            
            print("Waiting for new IP address...")
            for i in range(40):
                ip_after = get_public_ip()
                if ip_after and ip_after != ip_before:
                    print(f"SUCCESS: New IP is {ip_after}")
                    print(f"Time taken: {time.time() - start_time:.2f} seconds")
                    return True
                if ip_after == ip_before:
                    # Still same IP, wait a bit
                    pass
                time.sleep(1)
            
            print("Failed to get a new IP address within timeout.")
            return False
            
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    reset_modem_ip()
