# encoding=utf-8

"""
    @author: anzz
    @date: 2019/5/17
"""



### Job Maker Config ####
id = 1
chain_type = "bhd"
enabled = True

testnet = True # is using testnet3

# payout address
# the private key of my2dxGb5jz43ktwGxg2doUaEb9WhZ9PQ7K is cQAiutBRMq4wwC9JHeANQLttogZ2EXw9AgnGXMq5S3SAMmbX2oLd
payout_address = "my2dxGb5jz43ktwGxg2doUaEb9WhZ9PQ7K"
# coinbase info with location ID (https://github.com/btccom/btcpool/issues/36)
coinbase_info = "region1/Project BTCPool/"

# block version, default is 0 means use the version which returned by bitcoind
# or you can specify the version you want to signal.
# more info: https://github.com/bitcoin/bips/blob/master/bip-0009.mediawiki
# Example:
#  0                     : use bitcoind block version,
#  536870912(0x20000000) : bip9 support (with empty version bits)
#  536870914(0x20000002) : bip141(segwit), bit 1
#
block_version = 0

rawgbt_topic = "BtcRawGbt"


job_topic = "BtcJob"

job_interval = 20 # send stratum job interval (seconds)
max_job_delay = 20 # max job dealy (seconds)

# max non-empty gbt life cycle time (seconds)
gbt_life_time = 90

# max empty gbt life cycle time seconds
# CAUTION: the value SHOULD >= 10. If non-empty job not come in 10 seconds,
#          jobmaker will always make a previous height job until its arrival
empty_gbt_life_time = 15

# policy used to determine the pace of merge mining jobs to be sent.
# 0: merge mining `getwork` does not trigger job updates (RSK and Namecoin).
# 1: update job when the `notify` flag in RSK `getwork` is true or the block height in Namecoin `getwork` higher than before.
# 2: update job when the current block hash of a merge mining `getwork` is different from before (RSK and Namecoin).
merged_mining_notify = 1 # (1 is recommended and default)

zookeeper_lock_path = "/locks/jobmaker_btc"
file_last_job_time = "/work/btcpool/build/run_jobmaker/btc_lastjobtime.txt"