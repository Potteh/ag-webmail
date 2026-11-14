<?php
/**
 * AGMail branding plugin for Roundcube's Elastic skin.
 */
class agmailbranding extends rcube_plugin
{
    public $task = '.*';
    public function init()
    {
        $this->include_stylesheet('agmail.css');
        $this->add_hook('ready', [$this, 'branding']);
    }
    public function branding($args)
    {
        $rc = rcmail::get_instance();
        $rc->config->set('product_name', 'AGMail');
        $rc->config->set('skin_logo', ['*' => '/plugins/agmailbranding/agmail-logo.svg']);
        return $args;
    }
}
