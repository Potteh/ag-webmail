<?php
/**
 * AGMail branding plugin for Roundcube's Elastic skin.
 */
class agmailbranding extends rcube_plugin
{
    public $task = '.*';

    public function init()
    {
        // Set branding before Roundcube renders the layout. The "ready"
        // hook runs too late for the skin's logo template in some views.
        $rc = rcmail::get_instance();
        $rc->config->set('product_name', 'AGMail');
        $rc->config->set('skin_logo', [
            '*' => '/plugins/agmailbranding/agmail-logo.svg',
        ]);

        $this->include_stylesheet('agmail.css');
    }
}
