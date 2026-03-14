from chat.management.commands.run_bot import message_splitter


def test_message_splitter_short_text():
    text = 'Lorem ipsum dolor sit integer.'
    result = message_splitter(text)
    assert len(result) == 1
    assert result[0] == text


def test_message_splitter_long_text_hard_cut():
    text = 'A' * 5000
    result = message_splitter(text)
    assert len(result) == 2
    assert len(result[0]) == 4096


def test_message_splitter_5000_text():
    text =  ('Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer elementum fermentum rutrum. '
             'Etiam sit amet turpis eget enim sollicitudin commodo. Maecenas imperdiet tellus et magna ultrices '
            'vulputate. Ut ultrices iaculis justo eget tincidunt. Nulla facilisi. Quisque dictum eleifend gravida. '
            'Aenean pretium risus ut ornare imperdiet. Nam rutrum purus at quam sollicitudin sagittis ut ut justo. '
            'Suspendisse nec pulvinar diam. Etiam bibendum ipsum id risus dictum pulvinar. Morbi dignissim lorem '
            'magna. Nullam at cursus orci.) Aliquam erat volutpat. Donec ut aliquet neque. Donec luctus id ex at '
            'porttitor. Nullam a tristique lectus. Suspendisse tempor lobortis faucibus. Curabitur interdum lobortis '
            'justo. Sed tortor nibh, eleifend vitae purus at, porttitor blandit felis. Fusce ut vulputate orci. '
            'Donec tincidunt ultrices magna, ullamcorper dapibus nulla feugiat venenatis. Sed quis scelerisque metus, '
            'eget interdum tellus. Sed purus sem, ultrices ut fermentum non, bibendum vel ligula. Nulla non sapien '
            'sapien. Quisque ut orci in urna volutpat aliquam. Cras in pharetra odio. Suspendisse sagittis enim non '
            'nisl varius feugiat. Vivamus in turpis ultricies, ultricies neque id, imperdiet libero. Vestibulum viverra '
            'eleifend tellus id mollis. Fusce consequat maximus suscipit. Quisque interdum semper pellentesque. Donec '
            'sit amet orci placerat, fringilla leo id, egestas leo. Donec laoreet enim a orci facilisis, sit amet '
            'tincidunt quam elementum. Aenean cursus metus nulla, eu porta mauris maximus id. Nullam odio metus, '
            'commodo at odio quis, luctus semper libero. Sed quis dolor neque. Nam porttitor pulvinar libero id congue. '
            'Curabitur suscipit vitae purus eget aliquam. Sed eleifend eu mi ut gravida. Vivamus cursus velit at odio '
            'vestibulum, a iaculis lectus mollis. Mauris quis enim ac metus posuere auctor sed ac turpis. Nunc sit '
            'amet purus eu augue venenatis molestie. Nam egestas eu sem nec fringilla. Quisque id tellus gravida, '
            'congue tellus sed, semper diam. Etiam lobortis ex quis nisi commodo dapibus. Vestibulum in consequat nisl, '
            'et feugiat ipsum. Duis vitae dictum libero, vitae aliquet mauris. Quisque finibus tellus dui, consequat '
            'tempus ex hendrerit nec. Nulla lacus turpis, blandit quis tincidunt et, ultricies sit amet erat. Maecenas '
            'mollis non eros a consectetur. Phasellus suscipit posuere sapien, vitae cursus eros scelerisque in. '
            'Praesent orci tellus, porta non euismod mattis, placerat at lacus. Aliquam ornare, lacus at malesuada '
            'varius, nulla ex dapibus ligula, id molestie massa risus vel quam. Maecenas bibendum urna in odio blandit, '
            'fringilla consequat libero maximus. Aenean in augue ut augue tempor posuere. Fusce sagittis felis quam, '
            'vel tempor ligula congue vel. Fusce tincidunt non risus nec aliquet. Donec consectetur, felis ac pretium '
            'rutrum, nibh nisi mattis magna, id malesuada ligula orci eget leo. Ut maximus enim in magna blandit, eu '
            'efficitur enim ullamcorper. Pellentesque nec justo nisi. Nulla volutpat tincidunt felis in consequat. '
            'Nullam et velit mi. Duis sed lorem maximus, ultricies mauris non, tempor turpis. Nullam et tellus '
            'ultricies, cursus augue ac, faucibus elit. Aliquam ut aliquet eros. Suspendisse ultrices mollis lectus. '
            'Morbi at velit id urna sodales ultrices. Ut faucibus urna quis tincidunt viverra. Suspendisse in mi sit '
            'amet lacus varius dapibus. Donec semper lacinia libero, quis mattis mauris iaculis sit amet. Nulla '
            'convallis nec felis ut imperdiet. Nam in mi quis felis sodales tempus. Morbi cursus euismod ante, a '
            'lobortis nulla vestibulum non. Suspendisse porta porttitor diam, in volutpat turpis elementum non. Donec '
            'elementum a lectus ut facilisis. Aliquam erat volutpat. Proin id molestie felis. Fusce non erat eu dui '
            'vestibulum congue et laoreet erat. Quisque in orci facilisis, luctus velit feugiat, rutrum magna. Mauris '
            'dictum nibh nisi, et placerat mi sagittis vel. Sed rutrum eros et vehicula tempor. Aliquam iaculis metus '
            'in sem congue pellentesque. Donec purus turpis, sagittis imperdiet dui et, auctor tincidunt urna. Proin '
            'a justo gravida, blandit ligula eget, placerat dui. Sed eget bibendum purus. Sed rutrum nisl vel vehicula '
            'condimentum. Ut commodo sit amet risus vitae imperdiet. Nullam eu tristique nisi. Cras nec nibh sit amet '
            'quam semper vehicula id ac ipsum. Morbi orci dolor, euismod id nulla et, egestas maximus eros. Ut congue '
            'turpis porttitor dui faucibus imperdiet. Cras ultrices commodo efficitur. Fusce laoreet diam ac odio '
            'sodales, non sollicitudin magna efficitur. Mauris et imperdiet lacus. Cras sodales quam massa, eget '
            'iaculis urna vulputate eleifend. Aliquam erat volutpat. Morbi dictum lacinia condimentum. Donec justo '
            'risus, molestie sed rhoncus vel, molestie quis eros. Cras tempus metus vitae ullamcorper gravida. Nunc '
            'imperdiet molestie ante, eu semper sem. Proin lacinia nisl a nisi hendrerit tristique. Aliquam '
            'ullamcorper facilisis pellentesque. In id lorem lectus. Nunc eget imperdiet metus. In ullamcorper pulvinar '
            'suscipit. Nulla auctor massa eu mi ornare, vel pulvinar ante sagittis. Proin nisi.')
    result = message_splitter(text)
    assert len(result) == 2
    assert len(result[0]) <= 4096

