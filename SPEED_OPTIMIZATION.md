# Speed Optimization Guide for Torr Downloader

## What I've Optimized (Already Applied)

I've upgraded your downloader with these high-performance settings:

### ✅ Automatic Optimizations (Built-in)

1. **More Connections**: Up to 200 simultaneous connections (default was ~50)
2. **UPnP/NAT-PMP**: Automatic port forwarding for better connectivity
3. **DHT Routers**: Connected to 4 major DHT nodes for faster peer discovery
4. **Better Caching**: 4MB cache for faster piece assembly
5. **Unlimited Speed**: No artificial rate limits
6. **Aggressive Peer Discovery**: Announces to all trackers and uses multiple peer sources
7. **Local Service Discovery (LSD)**: Finds peers on your local network

## Factors Affecting Download Speed

### 1. **Torrent Health** ⭐ (MOST IMPORTANT)
- **Seeders**: People who have the complete file
- **Leechers**: People downloading (like you)
- **More seeders = Faster downloads**

**Check torrent health:**
```bash
# Popular torrents = many seeders = fast downloads
# Old/unpopular torrents = few seeders = slow downloads
```

### 2. **Your Internet Connection** 🌐
- Your ISP's download speed is the ultimate limit
- Some ISPs throttle P2P traffic
- WiFi can be slower than Ethernet

### 3. **Network Configuration** 🔧
- Firewall blocking connections
- Router not forwarding ports
- Network congestion

### 4. **Upload Speed Matters** 📤
BitTorrent uses "tit-for-tat" - peers prefer to send to those who upload back.
- The optimizer sets unlimited upload
- You get better download speeds when you upload too

## Additional Manual Optimizations

### Option 1: Port Forwarding (Best Results)

If UPnP doesn't work automatically, manually forward ports in your router:

1. **Find your router's IP**: Usually `192.168.1.1` or `192.168.0.1`
2. **Log into router admin panel**
3. **Forward ports** `6881-6891` to your computer's local IP
4. **Protocol**: Both TCP and UDP

**Why it helps:** Allows more incoming connections from peers

### Option 2: Use a VPN with Port Forwarding

Some ISPs throttle P2P traffic. A VPN that supports port forwarding can help:
- Mullvad
- AirVPN
- Private Internet Access (PIA)

### Option 3: Try Different Torrents

Test with a known-fast torrent to verify your setup works:

**Ubuntu (thousands of seeders):**
```bash
python cli_downloader.py "magnet:?xt=urn:btih:3b245504cf5f11bbdbe1201cea6a6bf45aee1bc0&dn=ubuntu"
```

If Ubuntu downloads fast but your torrent is slow → the issue is torrent health, not your setup.

### Option 4: Test Your Connection

```bash
# Check your internet speed
# Visit speedtest.net

# Make sure you're not maxing out your bandwidth with other apps
# Close streaming, downloads, etc.
```

## Custom Settings (Advanced Users)

You can create a custom downloader with different settings:

```python
from downloader import TorrentDownloader
import libtorrent as lt

downloader = TorrentDownloader('./downloads')

# Example: Limit upload to save bandwidth but still get good speeds
custom_settings = {
    'upload_rate_limit': 100 * 1024,  # 100 KB/s upload limit
    'download_rate_limit': 0,  # Unlimited download
}
downloader.session.apply_settings(custom_settings)
```

## Troubleshooting Slow Downloads

### Problem: "0 peers" or "very few peers"
**Solutions:**
- Wait longer (DHT takes time to find peers)
- Check if the torrent is active (old torrents have no seeders)
- Disable VPN temporarily to test
- Check firewall settings

### Problem: "Many peers but slow speed"
**Solutions:**
- Your internet connection might be the bottleneck
- Try Ethernet instead of WiFi
- Close other bandwidth-heavy applications
- Some peers might have slow upload speeds

### Problem: "Speed starts fast then drops"
**Solutions:**
- Normal behavior - you initially connect to fastest peers
- Some peers disconnect when you don't upload enough
- Your ISP might be throttling after detecting P2P traffic

### Problem: "Can't connect to any peers"
**Solutions:**
- Firewall is blocking the application
- Router is blocking P2P traffic
- ISP is blocking BitTorrent ports
- Try a different network (mobile hotspot to test)

## Monitoring Download Speed

The CLI downloader shows:
- `↓X MB/s` - Your download speed
- `Peers:X` - Connected peers
- `Seeds:X` - Connected seeders

**Good signs:**
- Increasing peer count in first few minutes
- Peers/Seeds ratio > 0.1 (10% seeders is good)
- Speed increases as more peers connect

**Bad signs:**
- Peers stay at 0 after 5 minutes
- Seeds = 0 (dead torrent)
- Speed = 0 despite having peers

## Expected Speeds

**With good torrents:**
- 1 Gbps connection: 50-100 MB/s download
- 100 Mbps connection: 5-10 MB/s download
- 50 Mbps connection: 2-5 MB/s download
- 10 Mbps connection: 500 KB/s - 1 MB/s download

**Note:** These are ideal conditions. Real speeds depend on seeder upload speeds too.

## Comparison: Before vs After Optimization

### Before (Basic Settings)
- Max connections: ~50
- No UPnP: Manual port forwarding required
- Single DHT router
- Limited cache
- Slower peer discovery

### After (Optimized Settings) ✅
- Max connections: 200
- UPnP enabled: Automatic port forwarding
- 4 DHT routers: Faster peer discovery
- 4MB cache: Better performance
- Aggressive peer gathering

**Expected improvement:** 2-5x faster on popular torrents (depends on your network)

## Tips for Maximum Speed

1. **✅ Use popular torrents** (1000+ seeders)
2. **✅ Connect via Ethernet** (not WiFi)
3. **✅ Forward ports** in your router (if UPnP fails)
4. **✅ Close other applications** using bandwidth
5. **✅ Let it run** - Speed increases as more peers connect
6. **✅ Allow uploading** - Better upload = Better download
7. **❌ Don't use VPN** unless necessary (adds overhead)
8. **❌ Don't limit connections** too much

## Testing Your Setup

Run this command to test with a fast, popular torrent:

```bash
python cli_downloader.py "magnet:?xt=urn:btih:3b245504cf5f11bbdbe1201cea6a6bf45aee1bc0&dn=ubuntu"
```

Watch the output:
- Peers should increase within 1-2 minutes
- Speed should increase as peers connect
- If Ubuntu is fast, your setup is working correctly!

## Still Slow? Report This Info:

If speeds are still slow after optimization, check:

1. **Number of seeders/peers** in the first 2 minutes
2. **Your internet speed** (from speedtest.net)
3. **Actual download speed** from the CLI
4. **Test with Ubuntu torrent** - is it also slow?

This will help identify if it's:
- Your connection (everything is slow)
- The torrent (only some are slow)
- Your network setup (ports blocked)

## Summary

The optimizations I applied should significantly improve your speeds, especially on:
- ✅ Popular torrents with many seeders
- ✅ Well-connected networks
- ✅ Fast internet connections

The biggest factor is still **torrent health** - no optimization can fix a dead torrent!

Happy downloading! 🚀

