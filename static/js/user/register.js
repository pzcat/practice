$(()=>{              // 整个页面加载完后执行的代码
    // 1. 点击刷新图片验证码
    $('.captcha-graph-img img').click(function(){
        $(this).attr('src', '/image_code/?rand=' + Math.random())     // this表示当前对象，即image
    });
    // 2.校验用户名
    // 定义一些状态变量
    let isUsernameReady = false,
        isPasswordReady = false,
        isMobileReady = false;
        // isSmsCodeReady = false;

    // 用户名校验，光标离开用户名输入框就校验用户名
    let $username = $('#username');
    $username.blur(fnCheckUsername);

    function fnCheckUsername(){
        // 校验用户名
        isUsernameReady = false;
        // 获取输入的用户名
        let sUsername = $username.val();

        if (sUsername ===''){                        // 用户名为空检测
            message.showError("用户名不能为空")
            return
        }
        if (!(/^\w{5,20}$/).test(sUsername)){
            message.showError("请输入5-20个字符的用户名")
            return
        }

        // 验证通过，发送ajax请求
        // 请求username/sUsername/ 对应的视图函数
        // 如果请求发送成果，浏览器会把response的结果返回给function的形参
        $.ajax({
            url: '/username/' + sUsername + '/',
            type:'GET',
            dataType: 'json',
            success: function(data){
                if (data.count !==0){
                    message.showError(data.username + '已经注册，请重新输入')
                } else{
                    message.showInfo(data.username + '用户名可用')
                    isUsernameReady = true
                }
            },
            error: function(){
                message.showError('服务器超时，请重试')
            }
        })

    }

    // 3. 检验密码是否一致
    let $passwordRepeat = $('input[name="password_repeat"]');
    $passwordRepeat.blur(fnCheckPassword);

    function fnCheckPassword(){
        isPasswordReady = false;
        let pwd = $('input[name="password"]').val();
        let pwdRepeat = $passwordRepeat.val();
        if (pwd ==='' || pwd ===''){
            message.showError("密码不能为空");
            return;
        }
        if (pwd !== pwdRepeat){
            message.showError('两次密码输入不一致');
            return;
        }
        if (pwd === pwdRepeat){
            isPasswordReady = true
        }

    }

    // 4. 手机号校验
    let $mobile = $('input[name="mobile"]');
    $mobile.blur(fnCheckMobile);

    function fnCheckMobile(){
        isMobileReady = false;
        let sMobile = $mobile.val();
        if (sMobile ===''){
            message.showError("手机号不能为空");
            return;
        }

        if (!(/^1[3-9]\d{9}$/).test(sMobile)){
            message.showError("手机号格式不正确");
            return
        }

        // 发送ajax
        $
            .ajax({
                url: '/mobile/' + sMobile + '/',
                type: 'GET',
                dataType: 'json'
            })
            .done((res)=>{                               // 发送成功的第二种写法，现在常用
                if (res.data.count !== 0){
                    message.showError("手机号已被注册，请重新输入");
                } else {
                    message.showInfo(res.data.mobile + "手机号可以使用");
                    isMobileReady = true;
                }
            })
            .fail(()=>{
                message.showError("服务器超时，请重试");
            })
    }

    // 5. 发送短信验证码
    let $smsButton = $('.sms-captcha');
    $smsButton.click(()=>{                           // 匿名函数
        // 拿到数据
        // 图形验证码
        let sCaptcha = $('input[name="captcha_graph"]').val();
        if (sCaptcha === ''){
            message.showError('请输入图形验证码');
            return
        }
        if (sCaptcha.length !== 4){
            message.showError('请输入4位图形验证码');
            return
        }
        // 判断手机号码是否准备好
        if (!isMobileReady){
            fnCheckMobile();
            return
        }

        $
            .ajax({
                url: '/sms_code/',
                type: 'POST',
                data: {
                    mobile: $mobile.val(),
                    captcha: sCaptcha
                },
                dataType: 'json'
            })
            .done((res)=>{
                if(res.errno !== '0' ){
                    message.showError(res.errmsg);
                } else {
                    message.showSuccess(res.errmsg);
                    $smsButton.attr('disabled', true);     // 发送按钮不能再点击
                    // 倒计时
                    var num = 60;      // 此处不能用let定义
                    // 设计计时器
                    let t = setInterval(function () {
                        $smsButton.html(num + '秒后重新发送');
                        if (num===1){
                            clearInterval(t);     // 停止计时器
                            $smsButton.removeAttr('disabled');
                            $smsButton.html('获取短信验证码')
                        }
                        num --;
                    }, 1000)
                }
            })
            .fail(()=>{
                message.showError("服务器超时，请重试")
            });

    });

    // 6. 注册
    let $submitBtn = $('.register-btn');
    $submitBtn.click((e)=>{          // 传入事件
        // 阻止默认提交
        e.preventDefault();
        // 校验数据
        // 1. 检查用户名
        if (!isUsernameReady){
            fnCheckUsername();
            return;
        }
        // 2. 检查密码
        if (!isPasswordReady){
            fnCheckPassword();
            return;
        }
        // 3. 检查电话号码
        if (!isMobileReady){
            fnCheckMobile();
            return;
        }
        // 4. 检查短信验证码
        let sSmsCode = $('input[name="sms_captcha"]').val();
        if (sSmsCode === ''){
            message.showError('短信验证码不能为空');
            return;
        }
        if (!(/^\d{4}$/).test(sSmsCode)){
            message.showError('短信验证码长度不正确，必须是4位数字')
        }
        // 5. 发送ajax
        $
            .ajax({
                url: '/user/register/',
                type: 'POST',
                data: {
                    username: $username.val(),
                    password: $('input[name="password"]').val(),
                    password_repeat: $passwordRepeat.val(),
                    mobile: $mobile.val(),
                    sms_code: sSmsCode
                },
                dataType: 'json'
            })
            .done((res)=>{
                if (res.errno ==='0'){
                    message.showSuccess(res.errmsg);
                    // 1.5秒后跳转到登录页面
                    setTimeout(()=>{
                        window.location.href = '/user/login/'
                    }, 1500)
                } else {
                    message.showError(res.errmsg);
                }
            })
            .fail(()=>{
                message.showError("服务器超时，请重试");
            })
    });


});