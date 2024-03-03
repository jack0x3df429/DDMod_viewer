from dddecoder import dddecoder

def handle_upload(file):
    ddd=dddecoder.decode_file(file)
    ddd.decode()
    ddd.data2json()
    ddd.encode("encode.json")

# 使用方式：
file = 'encode.json'
#file = 'persist.game.json'
#file = 'D:/Games/Steam/userdata/247796443/262060/remote/profile_0/persist.campaign_log.json'
#file = 'persist.tutorial.json'
handle_upload(file)

#pub fn name_hash(s: &'_ str) -> i32 {
#    s.bytes().fold(0i32, |acc, c| {
#        acc.wrapping_mul(53).wrapping_add(i32::from(c))
#    })
#}
#01101110000010001001011101111111
#11000111110001110101110101001100