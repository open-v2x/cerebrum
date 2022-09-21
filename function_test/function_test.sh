#!/bin/sh

export PYTHONPATH=$PYTHONPATH:`pwd`

get_config(){
    if [ ! -n "$ip" ] ;then
        echo "you have not set openv2x external ip!"
        exit 1
    fi
    if [ ! -n "$emqx_root" ] ;then
        echo "you have not set emqx root password!"
        exit 1
    fi
}

set_config(){
    #sed -i "s/host.*/host = \"$ip\"/" algorithm_functest/config/config.py
    ls function_test/*.yaml | xargs sed -i "s/host.*/host: $ip/" --
    ls function_test/*.yaml | xargs sed -i "s/password.*/password: $emqx_root/" --
}

verify_test(){
    #python3 algorithm_functest/common/pub.py
    ls function_test/*.yaml | xargs tavern-ci --
}

{
    get_config
    set_config
    verify_test
}
