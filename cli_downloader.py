#!/usr/bin/env python3
"""
CLI Torrent Downloader with beautiful progress bars and colored output
"""

import libtorrent as lt
import time
import os
import sys
from tqdm import tqdm
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)


def format_bytes(bytes_val):
    """Format bytes to human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} PB"


def format_time(seconds):
    """Format seconds to human-readable time"""
    if seconds == 0:
        return "N/A"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def download_torrent(magnet_link, download_path='./downloads'):
    """
    Download a torrent with beautiful CLI interface
    
    Args:
        magnet_link (str): The magnet link to download
        download_path (str): Path where files will be saved
    """
    # Create download directory
    if not os.path.exists(download_path):
        os.makedirs(download_path)
    
    print(f"{Fore.BLUE}🚀 Starting torrent download...")
    print(f"{Fore.CYAN}📁 Download location: {os.path.abspath(download_path)}\n")
    
    # Create session with optimized settings for faster downloads
    session = lt.session()
    session.listen_on(6881, 6891)
    
    # Apply high-performance settings
    settings = {
        # Connection settings - more connections = faster downloads
        'connections_limit': 200,
        'connection_speed': 50,
        
        # Per-torrent limits
        'max_out_request_queue': 500,
        'max_allowed_in_request_queue': 500,
        
        # Enable DHT, LSD, UPnP for better peer discovery
        'enable_dht': True,
        'enable_lsd': True,  # Local Service Discovery
        'enable_upnp': True,  # Automatic port forwarding
        'enable_natpmp': True,  # NAT-PMP port mapping
        
        # Unlimited download/upload (0 = unlimited)
        'download_rate_limit': 0,
        'upload_rate_limit': 0,
        
        # More peers
        'max_peerlist_size': 4000,
        'max_paused_peerlist_size': 4000,
        
        # Better tracker behavior
        'announce_to_all_trackers': True,
        'announce_to_all_tiers': True,
        
        # Optimize piece selection
        'strict_end_game_mode': True,
        
        # Performance optimizations
        'send_buffer_watermark': 500 * 1024,
        'cache_size': 256 * 16,  # 4 MB cache
        'active_downloads': 8,
        'active_limit': 15,
    }
    
    session.apply_settings(settings)
    
    # Add DHT routers for finding peers
    session.add_dht_router("router.bittorrent.com", 6881)
    session.add_dht_router("router.utorrent.com", 6881)
    session.add_dht_router("dht.transmissionbt.com", 6881)
    session.add_dht_router("dht.libtorrent.org", 25401)
    
    # Start services
    session.start_dht()
    session.start_lsd()
    session.start_upnp()
    session.start_natpmp()
    
    # Parse and add magnet link
    try:
        params = lt.parse_magnet_uri(magnet_link)
        params.save_path = download_path
        handle = session.add_torrent(params)
    except Exception as e:
        print(f"{Fore.RED}❌ Error parsing magnet link: {str(e)}")
        return
    
    # Wait for metadata
    print(f"{Fore.YELLOW}⏳ Fetching torrent metadata...")
    print(f"{Fore.CYAN}   (Connecting to peers via DHT and trackers...)\n")
    
    timeout = 60  # 60 second timeout
    start_time = time.time()
    last_peer_count = 0
    
    while not handle.status().has_metadata:
        if time.time() - start_time > timeout:
            print(f"\n{Fore.RED}❌ Timeout: Could not fetch metadata after 60 seconds")
            print(f"{Fore.YELLOW}   The torrent might be dead or have network issues")
            return
        
        status = handle.status()
        if status.num_peers != last_peer_count and status.num_peers > 0:
            print(f"{Fore.GREEN}   ✓ Connected to {status.num_peers} peer(s)...")
            last_peer_count = status.num_peers
        
        time.sleep(1)
    
    # Get torrent info
    torrent_info = handle.get_torrent_info()
    
    print(f"\n{Fore.GREEN}✅ Torrent found: {Style.BRIGHT}{torrent_info.name()}")
    print(f"{Fore.CYAN}   Files: {torrent_info.num_files()}")
    print(f"{Fore.CYAN}   Size: {format_bytes(torrent_info.total_size())}\n")
    
    # Create progress bar
    pbar = tqdm(
        total=100,
        desc="Downloading",
        unit="%",
        bar_format='{l_bar}{bar}| {n:.1f}% [{elapsed}<{remaining}, {rate_fmt}]'
    )
    
    # Download loop
    last_progress = 0
    try:
        while not handle.is_seed():
            status = handle.status()
            
            # Update progress bar
            current_progress = status.progress * 100
            if current_progress > last_progress:
                pbar.update(current_progress - last_progress)
                last_progress = current_progress
            
            # Update description with stats
            download_speed = format_bytes(status.download_rate) + "/s"
            upload_speed = format_bytes(status.upload_rate) + "/s"
            peers = status.num_peers
            seeds = status.num_seeds
            
            pbar.set_postfix_str(
                f"↓{download_speed} ↑{upload_speed} Peers:{peers} Seeds:{seeds}"
            )
            
            time.sleep(1)
        
        # Ensure progress bar reaches 100%
        if pbar.n < 100:
            pbar.update(100 - pbar.n)
        pbar.close()
        
        # Download complete
        print(f"\n{Fore.GREEN}{Style.BRIGHT}✨ Download complete!")
        print(f"{Fore.CYAN}📁 Files saved to: {os.path.abspath(download_path)}")
        print(f"\n{Fore.CYAN}Downloaded files:")
        
        for i in range(torrent_info.num_files()):
            file_info = torrent_info.file_at(i)
            print(f"{Fore.YELLOW}   • {file_info.path} ({format_bytes(file_info.size)})")
        
        print()
        
    except KeyboardInterrupt:
        pbar.close()
        print(f"\n\n{Fore.YELLOW}⚠️  Download cancelled by user")
        handle.pause()
        session.pause()
    except Exception as e:
        pbar.close()
        print(f"\n\n{Fore.RED}❌ Error: {str(e)}")
    finally:
        # Clean shutdown
        session.pause()


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print(f"{Fore.RED}❌ Error: Please provide a magnet link")
        print(f"{Fore.YELLOW}Usage: python cli_downloader.py <magnet-link> [download-path]")
        print(f"{Fore.YELLOW}Example: python cli_downloader.py \"magnet:?xt=urn:btih:...\" ./downloads")
        sys.exit(1)
    
    magnet_link = sys.argv[1]
    download_path = sys.argv[2] if len(sys.argv) > 2 else './downloads'
    
    download_torrent(magnet_link, download_path)


if __name__ == '__main__':
    main()

