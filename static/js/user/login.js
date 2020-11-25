$(function(){
    let $loginBtn = $('.login-btn');             // 获取登录按钮元素
    $loginBtn.click(function(e){
        // 阻止submit提交
        e.preventDefault();

        // 1. 校验账户
        let sAccount = $('input[name="account"]').val();
        if (sAccount ===''){
            message.showError('用户账户不能为空');
            return
        }
        if (!(/^1[3-9]\d{9}$/).test(sAccount) && !(/^\w{5,20}$/).test(sAccount)){
            message.showError('账户格式不正确');
            return
        }

        // 2. 校验密码
        let sPassword = $('input[name="password"]').val();
        if (sPassword ===''){
            message.showError('密码不能为空');
            return
        }

        // 3. 获取remember参数
        let bRemember = $('input[name="remember"]').is(':checked');

        // 4. 发送ajax
        $.ajax({
            url: '/user/login/',
            type: 'POST',
            dataType: 'json',
            data: {
                account: sAccount,
                password: sPassword,
                remember: bRemember
            },
            success: function(res){
                if (res.errno === '0'){
                    message.showSuccess('登录成功');
                    setTimeout(function () {
                        // 注册成功之后重定向到打开登录页面之前的页面
                        // document.referrer 登录前所在页面
                        // document.referrer.includes('/user/login/') 刷新登录页面
                        // document.referrer.includes('/user/register/')之前在注册页面
                        if (!document.referrer || document.referrer.includes('/user/login/')
                        || document.referrer.includes('/user/register/')){
                            window.location.href = '/index/';
                        } else {
                            window.location.href = document.referrer
                        }
                    }, 3000)
                } else {
                    message.showError(res.errmsg)
                }
            },
            error: function(){
                message.showError('服务器超时，请重试')
            }
        })

    })
});