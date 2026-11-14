<?php
// Additional Roundcube configuration loaded only when explicitly included.
$config['product_name'] = 'AGMail';
$config['support_url'] = '';
$config['skin'] = 'elastic';
$config['des_key'] = getenv('ROUNDCUBE_DES_KEY') ?: 'REPLACE_WITH_RANDOM_24_CHAR_KEY';
