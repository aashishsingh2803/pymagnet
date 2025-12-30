#!/usr/bin/env python3
"""
Core TorrentDownloader class for downloading files from magnet links
"""

import libtorrent as lt
import time
import os


class TorrentDownloader:
    """A simple class to download files from magnet links using libtorrent"""
    
    def __init__(self, download_path='./downloads'):
        """
        Initialize the TorrentDownloader
        
        Args:
            download_path (str): Path where downloaded files will be saved
        """
        self.download_path = download_path
        
        # Create session with optimized settings
        self.session = lt.session()
        self.session.listen_on(6881, 6891)
        
        # Apply high-performance settings
        settings = {
            # Connection settings
            'connections_limit': 200,
            'connection_speed': 50,  # Rate at which new connections are tried
            
            # Per-torrent connection limits
            'max_out_request_queue': 500,
            'max_allowed_in_request_queue': 500,
            
            # DHT settings for finding peers without trackers
            'enable_dht': True,
            'enable_lsd': True,  # Local Service Discovery
            'enable_upnp': True,  # UPnP port mapping
            'enable_natpmp': True,  # NAT-PMP port mapping
            
            # Peer exchange
            'peer_tos': 0x00,
            
            # Download/upload settings
            'download_rate_limit': 0,  # 0 = unlimited
            'upload_rate_limit': 0,    # 0 = unlimited (helps get more peers)
            
            # Request more peers
            'max_peerlist_size': 4000,
            'max_paused_peerlist_size': 4000,
            
            # Optimize piece selection
            'strict_end_game_mode': True,
            'announce_to_all_trackers': True,
            'announce_to_all_tiers': True,
            
            # Improve seeding behavior (helps get pieces faster)
            'seed_time_limit': 0,
            'seed_time_ratio_limit': 0,
            
            # Handshake timeout
            'handshake_timeout': 10,
            
            # Optimizations
            'mixed_mode_algorithm': 0,  # prefer TCP
            'send_buffer_watermark': 500 * 1024,
            'cache_size': 256 * 16,  # 256 * 16 KB = 4 MB cache
            'active_downloads': 8,
            'active_limit': 15,
        }
        
        # Apply settings
        self.session.apply_settings(settings)
        
        # Start DHT
        self.session.add_dht_router("router.bittorrent.com", 6881)
        self.session.add_dht_router("router.utorrent.com", 6881)
        self.session.add_dht_router("dht.transmissionbt.com", 6881)
        self.session.add_dht_router("dht.libtorrent.org", 25401)
        
        self.session.start_dht()
        self.session.start_lsd()
        self.session.start_upnp()
        self.session.start_natpmp()
        
        # Create download directory if it doesn't exist
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
    
    def download(self, magnet_link, on_progress=None, on_metadata=None):
        """
        Download a torrent from a magnet link
        
        Args:
            magnet_link (str): The magnet link to download
            on_progress (callable): Optional callback for progress updates
            on_metadata (callable): Optional callback when metadata is received
            
        Returns:
            dict: Information about the downloaded torrent
        """
        # Parse magnet link
        params = lt.parse_magnet_uri(magnet_link)
        params.save_path = self.download_path
        
        # Add torrent to session
        handle = self.session.add_torrent(params)
        
        # Wait for metadata
        print("Fetching torrent metadata...")
        print("(This may take a moment while connecting to peers...)")
        
        timeout = 60  # 60 second timeout
        start_time = time.time()
        
        while not handle.status().has_metadata:
            if time.time() - start_time > timeout:
                raise TimeoutError("Could not fetch metadata. The torrent might be dead or network issues.")
            
            status = handle.status()
            if status.num_peers > 0:
                print(f"  Connected to {status.num_peers} peer(s), waiting for metadata...")
            
            time.sleep(1)
        
        # Get torrent info
        torrent_info = handle.get_torrent_info()
        
        # Call metadata callback if provided
        if on_metadata:
            metadata = {
                'name': torrent_info.name(),
                'num_files': torrent_info.num_files(),
                'total_size': torrent_info.total_size(),
                'info_hash': str(handle.info_hash())
            }
            on_metadata(metadata)
        
        # Download loop
        print(f"Starting download: {torrent_info.name()}")
        
        while not handle.is_seed():
            status = handle.status()
            
            # Call progress callback if provided
            if on_progress:
                progress_info = {
                    'progress': status.progress * 100,
                    'download_rate': status.download_rate,
                    'upload_rate': status.upload_rate,
                    'num_peers': status.num_peers,
                    'num_seeds': status.num_seeds,
                    'total_done': status.total_done,
                    'total_wanted': status.total_wanted,
                    'state': str(status.state)
                }
                on_progress(progress_info)
            
            time.sleep(1)
        
        # Download complete
        files = []
        for i in range(torrent_info.num_files()):
            file_info = torrent_info.file_at(i)
            files.append({
                'name': file_info.path,
                'size': file_info.size
            })
        
        result = {
            'name': torrent_info.name(),
            'files': files,
            'download_path': os.path.abspath(self.download_path)
        }
        
        return result
    
    def get_info(self, magnet_link):
        """
        Get information about a torrent without downloading
        
        Args:
            magnet_link (str): The magnet link to inspect
            
        Returns:
            dict: Metadata about the torrent
        """
        params = lt.parse_magnet_uri(magnet_link)
        params.save_path = self.download_path
        
        handle = self.session.add_torrent(params)
        
        # Wait for metadata
        timeout = 60  # 60 second timeout
        start_time = time.time()
        
        while not handle.status().has_metadata:
            if time.time() - start_time > timeout:
                raise TimeoutError("Could not fetch metadata. The torrent might be dead or network issues.")
            time.sleep(1)
        
        torrent_info = handle.get_torrent_info()
        
        files = []
        for i in range(torrent_info.num_files()):
            file_info = torrent_info.file_at(i)
            files.append({
                'name': file_info.path,
                'size': file_info.size
            })
        
        info = {
            'name': torrent_info.name(),
            'files': files,
            'total_size': torrent_info.total_size(),
            'info_hash': str(handle.info_hash())
        }
        
        # Remove the torrent after getting info
        self.session.remove_torrent(handle)
        
        return info
    
    def shutdown(self):
        """Clean up and shutdown the session"""
        # Pause all torrents
        torrents = self.session.get_torrents()
        for torrent in torrents:
            torrent.pause()
        
        # Save resume data
        self.session.pause()
        time.sleep(1)


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python downloader.py <magnet-link>")
        sys.exit(1)
    
    magnet_link = sys.argv[1]
    download_path = sys.argv[2] if len(sys.argv) > 2 else './downloads'
    
    downloader = TorrentDownloader(download_path)
    
    def progress_callback(progress):
        print(f"Progress: {progress['progress']:.2f}% - "
              f"Speed: {progress['download_rate'] / 1024:.2f} KB/s - "
              f"Peers: {progress['num_peers']}")
    
    def metadata_callback(metadata):
        print(f"\nTorrent found: {metadata['name']}")
        print(f"Files: {metadata['num_files']}")
        print(f"Size: {metadata['total_size'] / (1024*1024):.2f} MB\n")
    
    try:
        result = downloader.download(
            magnet_link,
            on_progress=progress_callback,
            on_metadata=metadata_callback
        )
        
        print("\n✅ Download complete!")
        print(f"📁 Files saved to: {result['download_path']}")
        print("\nDownloaded files:")
        for file in result['files']:
            print(f"  • {file['name']} ({file['size'] / (1024*1024):.2f} MB)")
        
    except KeyboardInterrupt:
        print("\n⚠️  Download cancelled by user")
        downloader.shutdown()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        downloader.shutdown()
        sys.exit(1)

