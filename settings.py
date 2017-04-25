
# queue redis nodes
redis_nodes = [{"host": "192.168.207.187","port": "9100"}]

proxy_http = "http://192.168.201.39:8882"

mongo_uri = 'mongodb://192.168.207.213:27016'
send_msg_mongo_db_name = 'msg_sended'
calendar_mongo_db_name = 'calendar'

msg_queue_name = "wechat_msg"

# remove
mongo_user_name = 'scrapyer'
mongo_password = 'scrapy'
mongo_admin_db_name = 'admin'

clients = {
    "IOS": "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"
}

queue_api_base = "http://192.168.207.187:9910/crawltunnel/transport/192.168.207.187:9810/api/v1"
queue_api_base = "http://192.168.207.187:9810/api/v1"
