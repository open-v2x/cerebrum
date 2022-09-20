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
    x=$(ls function_test/*.tavern);for i in $x;do sed "s/host.*/host: $ip/" $i > ${i}.template;done
    x=$(ls function_test/*.tavern);for i in $x;do sed "s/password.*/password: $emqx_root/" ${i}.template > $i.yaml;done
    rm -rf function_test/*.template
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