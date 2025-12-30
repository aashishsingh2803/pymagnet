# Torr - Simple Torrent Downloader (Python)

A simple and easy-to-use torrent downloader that works with magnet links. Built with Python and libtorrent.

## Features

- ✨ Download files from magnet links
- 📊 Real-time progress tracking with beautiful progress bars
- 👥 Peer and seed connection information
- 🎨 Colorful CLI interface
- 📦 Programmatic API for integration into other projects
- ⚡ Fast and efficient using libtorrent
- 🚀 **Optimized for maximum download speed** (UPnP, DHT, 200 connections)
- 🔧 Automatic port forwarding and peer discovery

## Screenshot

![Torrent Downloader Interface](screenshot/Screenshot1.png)

## Requirements

- Python 3.7 or higher
- pip (Python package manager)

## Installation

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note:** Installing `libtorrent` might require compilation on some systems. If you encounter issues:

**On macOS:**
```bash
brew install libtorrent-rasterbar
pip install libtorrent
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install python3-libtorrent
# OR
pip install libtorrent
```

**On Windows:**
```bash
pip install libtorrent
```

## Usage

### Method 1: CLI Downloader (Recommended)

```bash
python cli_downloader.py "<magnet-link>" [download-path]
```

**Example:**
```bash
python cli_downloader.py "magnet:?xt=urn:btih:..." ./my-downloads
```

If you don't specify a download path, files will be saved to `./downloads`

### Method 2: Using the Downloader Class

Create your own Python script:

```python
from downloader import TorrentDownloader

# Create downloader instance
downloader = TorrentDownloader('./downloads')

# Define callbacks
def on_metadata(metadata):
    print(f"Downloading: {metadata['name']}")
    print(f"Size: {metadata['total_size'] / (1024*1024):.2f} MB")

def on_progress(progress):
    print(f"Progress: {progress['progress']:.2f}%")
    print(f"Speed: {progress['download_rate'] / 1024:.2f} KB/s")
    print(f"Peers: {progress['num_peers']}")

# Download
magnet_link = "magnet:?xt=urn:btih:..."
result = downloader.download(
    magnet_link,
    on_metadata=on_metadata,
    on_progress=on_progress
)

print(f"Download complete! Files: {result['files']}")
```

### Method 3: Quick Download (Basic)

```bash
python downloader.py "<magnet-link>" [download-path]
```

## How It Works

### Step-by-Step Process:

1. **Magnet Link Input**: You provide a magnet link (starting with `magnet:?`)

2. **Libtorrent Session**: The application creates a libtorrent session that:
   - Parses the magnet link
   - Connects to DHT (Distributed Hash Table) to find peers
   - Establishes connections with peers who have the file

3. **Metadata Retrieval**:
   - Contacts peers to get torrent metadata
   - Retrieves file information without downloading

4. **Download Process**:
   - Discovers and connects to peers and seeders
   - Downloads file pieces from multiple sources simultaneously
   - Verifies each piece using cryptographic hashes (built into BitTorrent protocol)
   - Assembles pieces into complete files

5. **Progress Tracking**: Shows real-time information:
   - Download progress percentage
   - Download and upload speeds
   - Number of connected peers and seeders
   - Estimated time remaining

6. **File Saving**: Once complete, files are saved to your specified directory

## Understanding Magnet Links

A magnet link looks like this:
```
magnet:?xt=urn:btih:HASH&dn=NAME&tr=TRACKER
```

Components:
- `xt`: eXact Topic (the file hash - this is the unique identifier)
- `dn`: Display Name (filename)
- `tr`: Tracker URL (optional, DHT can work without it)

## Example Magnet Links for Testing

You can test with these legal, open-source torrents:

**Ubuntu OS** (free and legal):
```
magnet:?xt=urn:btih:3b245504cf5f11bbdbe1201cea6a6bf45aee1bc0&dn=ubuntu
```

**Sintel Movie** (Creative Commons):
```
magnet:?xt=urn:btih:08ada5a7a6183aae1e09d831df6748d566095a10&dn=Sintel
```

**Big Buck Bunny** (Creative Commons):
```
magnet:?xt=urn:btih:dd8255ecdc7ca55fb0bbf81323d87062db1f6d1c&dn=Big+Buck+Bunny
```

## Project Structure

```
torr/
├── requirements.txt      # Python dependencies
├── cli_downloader.py     # CLI interface with progress bars and colors
├── downloader.py         # Core TorrentDownloader class
├── downloads/            # Default download directory (created automatically)
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## API Reference

### TorrentDownloader Class

Located in `downloader.py`

#### Constructor
```python
TorrentDownloader(download_path='./downloads')
```

#### Methods

**download(magnet_link, on_progress=None, on_metadata=None)**
- Downloads a torrent from a magnet link
- Args:
  - `magnet_link` (str): The magnet link
  - `on_progress` (callable): Optional callback for progress updates
  - `on_metadata` (callable): Optional callback when metadata is received
- Returns: dict with download information

**get_info(magnet_link)**
- Gets information about a torrent without downloading
- Args:
  - `magnet_link` (str): The magnet link
- Returns: dict with metadata

**shutdown()**
- Cleans up and shuts down the session

## CLI Features

The `cli_downloader.py` provides:
- 🎨 Colorful output using colorama
- 📊 Real-time progress bars using tqdm
- 📈 Download/upload speed tracking
- 👥 Peer and seed counts
- ⏱️ Time remaining estimates
- 🎯 Clear error messages

## Troubleshooting

### Installation Issues with libtorrent

If `pip install libtorrent` fails, try:
1. Install system dependencies first (see Installation section)
2. Use your system's package manager
3. Try `pip install python-libtorrent` instead
4. On Windows, download pre-built wheels from unofficial sources

### No peers found
- Make sure your internet connection is working
- Some networks/firewalls block P2P traffic (try a different network)
- The torrent might be old or have no active seeders
- Wait a bit longer - it can take time to find peers

### Slow download speeds

**The downloader is already optimized!** However, speed depends on:
- **Torrent health** (number of seeders) - MOST IMPORTANT
- Your internet speed
- Network configuration (firewall, router)
- ISP throttling of P2P traffic

**📖 See [SPEED_OPTIMIZATION.md](SPEED_OPTIMIZATION.md) for detailed optimization guide!**

Quick tips:
- Test with a popular torrent (e.g., Ubuntu) to verify your setup
- Make sure ports 6881-6891 aren't blocked by firewall
- Use Ethernet instead of WiFi if possible
- The optimizer already enables UPnP for automatic port forwarding

### Permission errors
- Make sure you have write permissions for the download directory
- Try running with appropriate permissions
- Specify a different download path

### Port binding errors
- The default ports (6881-6891) might be in use
- Close other torrent clients
- The program will try multiple ports automatically

## Performance Tips

1. **Better connectivity**: Forward ports 6881-6891 in your router
2. **More peers**: Use popular torrents with many seeders
3. **Faster downloads**: Close other applications using bandwidth
4. **Resume downloads**: The session data is saved automatically

## Legal Notice

⚠️ **Important**: This tool is for downloading legal content only. Make sure you have the right to download any content before using this tool. Respect copyright laws in your jurisdiction. The creator is not responsible for any misuse of this software.

## Technologies Used

- **Python 3**: Programming language
- **libtorrent**: High-performance C++ BitTorrent library with Python bindings
- **tqdm**: Progress bars for Python
- **colorama**: Colored terminal output (cross-platform)

## How BitTorrent Works

BitTorrent is a peer-to-peer (P2P) file sharing protocol:
1. Files are split into small pieces
2. Each piece has a cryptographic hash for verification
3. Peers download different pieces from different sources
4. Peers also upload pieces they have to others
5. This distributed approach is very efficient and fast

## Contributing

Feel free to submit issues and pull requests!

## License

MIT License - Feel free to use and modify as needed.

## Future Enhancements

Potential features to add:
- [ ] Web interface
- [ ] Queue management for multiple downloads
- [ ] Bandwidth limiting
- [ ] Pause/resume functionality
- [ ] Torrent file support (not just magnets)
- [ ] Selective file downloading
- [ ] Configuration file support

## Support

If you encounter any issues:
1. Check the Troubleshooting section
2. Ensure all dependencies are installed correctly
3. Verify your magnet link is valid
4. Check your network connection and firewall settings

Happy downloading! 🚀
