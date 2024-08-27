static void mac80211_hwsim_monitor_rx(struct ieee80211_hw *hw,
				      struct sk_buff *tx_skb,
				      struct ieee80211_channel *chan)
{
	// Define the original and new MAC addresses
	u8 orig_addr[ETH_ALEN] = {0x02, 0x00, 0x00, 0x00, 0x01, 0x00}; // Original MAC address
	u8 new_addr[ETH_ALEN] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55}; // X MAC address
	struct ieee80211_hdr *mac_hdr;
	struct mac80211_hwsim_data *data = hw->priv;
	struct sk_buff *skb;
	struct hwsim_radiotap_hdr *hdr;
	u16 flags;
	struct ieee80211_tx_info *info = IEEE80211_SKB_CB(tx_skb);
	struct ieee80211_rate *txrate = ieee80211_get_tx_rate(hw, info);
	
	mac_hdr = (struct ieee80211_hdr *)(tx_skb->data + tx_skb->mac_len);

	
	

	if (WARN_ON(!txrate))
		return;

	if (!netif_running(hwsim_mon))
		return;

	skb = skb_copy_expand(tx_skb, sizeof(*hdr), 0, GFP_ATOMIC);
	if (skb == NULL)
		return;

	hdr = skb_push(skb, sizeof(*hdr));
	hdr->hdr.it_version = PKTHDR_RADIOTAP_VERSION;
	hdr->hdr.it_pad = 0;
	hdr->hdr.it_len = cpu_to_le16(sizeof(*hdr));
	hdr->hdr.it_present = cpu_to_le32((1 << IEEE80211_RADIOTAP_FLAGS) |
					  (1 << IEEE80211_RADIOTAP_RATE) |
					  (1 << IEEE80211_RADIOTAP_TSFT) |
					  (1 << IEEE80211_RADIOTAP_CHANNEL));
	hdr->rt_tsft = __mac80211_hwsim_get_tsf(data);
	hdr->rt_flags = 0;
	hdr->rt_rate = txrate->bitrate / 5;
	hdr->rt_channel = cpu_to_le16(chan->center_freq);
	flags = IEEE80211_CHAN_2GHZ;
	if (txrate->flags & IEEE80211_RATE_ERP_G)
		flags |= IEEE80211_CHAN_OFDM;
	else
		flags |= IEEE80211_CHAN_CCK;
	hdr->rt_chbitmask = cpu_to_le16(flags);

	skb->dev = hwsim_mon;
	skb_reset_mac_header(skb);
	skb->ip_summed = CHECKSUM_UNNECESSARY;
	skb->pkt_type = PACKET_OTHERHOST;
	skb->protocol = htons(ETH_P_802_2);
	memset(skb->cb, 0, sizeof(skb->cb));
	
	//mac address change here
	// Check if the source MAC address is the original MAC address
	if (memcmp(mac_hdr->addr2, orig_addr, ETH_ALEN) == 0) {
    	// Change the source MAC address to X
    	memcpy(mac_hdr->addr2, new_addr, ETH_ALEN);
    	//printk(KERN_DEBUG "Source MAC address changed to %pM in function tx 1\n", mac_hdr->addr2);
	}

	// Check if the destination MAC address is the original MAC address
	
	if (memcmp(mac_hdr->addr1, orig_addr, ETH_ALEN) == 0) {
    	// Change the destination MAC address to X
    	memcpy(mac_hdr->addr1, new_addr, ETH_ALEN);
    	//printk(KERN_DEBUG "Destination MAC address changed to %pM in function tx 2\n", mac_hdr->addr1);
	}
	netif_rx(skb);
}















// Define the original and new MAC addresses
    //u8 orig_addr[ETH_ALEN] = {0x02, 0x00, 0x00, 0x00, 0x01, 0x00}; // Original MAC address
    //u8 new_addr[ETH_ALEN] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55}; // X MAC address
    
    
    
//struct ieee80211_hdr *mac_hdr; // Declare hdr here


mac_hdr = (struct ieee80211_hdr *)skb->data; // Assign hdr here

	
    // Check if the source MAC address is the original MAC address
    if (memcmp(mac_hdr->addr2, orig_addr, ETH_ALEN) == 0) {
        // Change the source MAC address to X
        memcpy(mac_hdr->addr2, new_addr, ETH_ALEN);
    }

    // Check if the destination MAC address is the original MAC address
    if (memcmp(mac_hdr->addr1, orig_addr, ETH_ALEN) == 0) {
        // Change the destination MAC address to X
        memcpy(mac_hdr->addr1, new_addr, ETH_ALEN);
    }




static void mac80211_hwsim_tx_frame(struct ieee80211_hw *hw,
				    struct sk_buff *skb,
				    struct ieee80211_channel *chan)
{
	// Define the original and new MAC addresses
	//u8 orig_addr[ETH_ALEN] = {0x02, 0x00, 0x00, 0x00, 0x01, 0x00}; // Original MAC address
	//u8 new_addr[ETH_ALEN] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55}; // X MAC address
	struct mac80211_hwsim_data *data = hw->priv;
	//struct ieee80211_hdr *mac_hdr; // Declare hdr here
	u32 _pid = READ_ONCE(data->wmediumd);

	//LOG_FUNC;
	if (ieee80211_hw_check(hw, SUPPORTS_RC_TABLE)) {
		struct ieee80211_tx_info *txi = IEEE80211_SKB_CB(skb);
		ieee80211_get_tx_rates(txi->control.vif, NULL, skb,
				       txi->control.rates,
				       ARRAY_SIZE(txi->control.rates));
	}

	mac80211_hwsim_monitor_rx(hw, skb, chan);

	/*
	//packet address changes here 

	mac_hdr = (struct ieee80211_hdr *)skb->data; // Assign hdr here

    // Check if the source MAC address is the original MAC address
    if (memcmp(mac_hdr->addr2, orig_addr, ETH_ALEN) == 0) {
        // Change the source MAC address to X
        memcpy(mac_hdr->addr2, new_addr, ETH_ALEN);
    }

    // Check if the destination MAC address is the original MAC address
    if (memcmp(mac_hdr->addr1, orig_addr, ETH_ALEN) == 0) {
        // Change the destination MAC address to X
        memcpy(mac_hdr->addr1, new_addr, ETH_ALEN);
    }

	*/
	if (_pid)
		return mac80211_hwsim_tx_frame_nl(hw, skb, _pid);

	mac80211_hwsim_tx_frame_no_nl(hw, skb, chan);
	dev_kfree_skb(skb);
}


static void mac80211_hwsim_tx(struct ieee80211_hw *hw,
			      struct ieee80211_tx_control *control,
			      struct sk_buff *skb)
{
	// Define the original and new MAC addresses
	u8 orig_addr[ETH_ALEN] = {0x02, 0x00, 0x00, 0x00, 0x01, 0x00}; // Original MAC address
	u8 new_addr[ETH_ALEN] = {0x00, 0x11, 0x22, 0x33, 0x44, 0x55}; // X MAC address
	struct ieee80211_hdr *mac_hdr;
	struct mac80211_hwsim_data *data = hw->priv;
	struct ieee80211_tx_info *txi = IEEE80211_SKB_CB(skb);
	//struct ieee80211_hdr *hdr = (void *)skb->data;
	struct ieee80211_chanctx_conf *chanctx_conf;
	struct ieee80211_channel *channel;
	//rathan wrote below line 
	struct ieee80211_hdr *hdr = (struct ieee80211_hdr *)skb->data;
	bool ack;
	u32 _portid;

	mac_hdr = (struct ieee80211_hdr *)(skb->data + skb->mac_len);
	


	// Check if the source MAC address is the original MAC address
	if (memcmp(mac_hdr->addr2, orig_addr, ETH_ALEN) == 0) {
    	// Change the source MAC address to X
    	memcpy(mac_hdr->addr2, new_addr, ETH_ALEN);
    	printk(KERN_DEBUG "Source MAC address changed to %pM in function tx 1\n", mac_hdr->addr2);
	}

	// Check if the destination MAC address is the original MAC address
	
	if (memcmp(mac_hdr->addr1, orig_addr, ETH_ALEN) == 0) {
    	// Change the destination MAC address to X
    	memcpy(mac_hdr->addr1, new_addr, ETH_ALEN);
    	printk(KERN_DEBUG "Destination MAC address changed to %pM in function tx 2\n", mac_hdr->addr1);
	}


	if (WARN_ON(skb->len < 10)) {
		/* Should not happen; just a sanity check for addr1 use */
		ieee80211_free_txskb(hw, skb);
		return;
	}

	if (!data->use_chanctx) {
		channel = data->channel;
	} else if (txi->hw_queue == 4) {
		channel = data->tmp_chan;
	} else {
		chanctx_conf = rcu_dereference(txi->control.vif->chanctx_conf);
		if (chanctx_conf)
			channel = chanctx_conf->def.chan;
		else
			channel = NULL;
	}

	if (WARN(!channel, "TX w/o channel - queue = %d\n", txi->hw_queue)) {
		ieee80211_free_txskb(hw, skb);
		return;
	}

	if (data->idle && !data->tmp_chan) {
		wiphy_dbg(hw->wiphy, "Trying to TX when idle - reject\n");
		ieee80211_free_txskb(hw, skb);
		return;
	}

	if (txi->control.vif)
		hwsim_check_magic(txi->control.vif);
	if (control->sta)
		hwsim_check_sta_magic(control->sta);

	if (ieee80211_hw_check(hw, SUPPORTS_RC_TABLE))
		ieee80211_get_tx_rates(txi->control.vif, control->sta, skb,
				       txi->control.rates,
				       ARRAY_SIZE(txi->control.rates));

	if (skb->len >= 24 + 8 &&
	    ieee80211_is_probe_resp(hdr->frame_control)) {
		/* fake header transmission time */
		struct ieee80211_mgmt *mgmt;
		struct ieee80211_rate *txrate;
		u64 ts;

		mgmt = (struct ieee80211_mgmt *)skb->data;
		txrate = ieee80211_get_tx_rate(hw, txi);
		ts = mac80211_hwsim_get_tsf_raw();
		mgmt->u.probe_resp.timestamp =
			cpu_to_le64(ts + data->tsf_offset +
				    24 * 8 * 10 / txrate->bitrate);
	}

	mac80211_hwsim_monitor_rx(hw, skb, channel);

	/* wmediumd mode check */
	_portid = READ_ONCE(data->wmediumd);

	//rathan 



	if (_portid)
		return mac80211_hwsim_tx_frame_nl(hw, skb, _portid);

	/* NO wmediumd detected, perfect medium simulation */
	data->tx_pkts++;
	data->tx_bytes += skb->len;
	ack = mac80211_hwsim_tx_frame_no_nl(hw, skb, channel);

	if (ack && skb->len >= 16)
		mac80211_hwsim_monitor_ack(channel, hdr->addr2);

	ieee80211_tx_info_clear_status(txi);

	/* frame was transmitted at most favorable rate at first attempt */
	txi->control.rates[0].count = 1;
	txi->control.rates[1].idx = -1;

	if (!(txi->flags & IEEE80211_TX_CTL_NO_ACK) && ack)
		txi->flags |= IEEE80211_TX_STAT_ACK;
	ieee80211_tx_status_irqsafe(hw, skb);
}


