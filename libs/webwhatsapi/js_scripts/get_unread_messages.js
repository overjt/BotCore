var Chats = Store.Chat.models;
var Output = [];

function isChatMessage(message) {
    if (message.__x_isSentByMe) {
        return false;
    }
    if (message.__x_isNotification) {
        return false;
    }
    if (!message.__x_isUserCreatedType) {
        return false;
    }
    return true;
}

for (chat in Chats) {
    if (isNaN(chat)) {
        continue;
    };
    var temp = {};
    temp.contact = Chats[chat].__x_formattedTitle;
    temp.id = Chats[chat].__x_id;
    temp.messages = [];
    var messages = Chats[chat].msgs.models;
    for (var i = messages.length - 1; i >= 0; i--) {
        if (!messages[i].__x_isNewMsg) {
            break;
        } else {
            if (!isChatMessage(messages[i])) {
                continue
            }
            var sender = {
                "id": messages[i].__x_senderObj.__x_id,
                "name": messages[i].__x_senderObj.__x_notifyName || messages[i].__x_senderObj.__x_formattedName,
                "customName": messages[i].__x_senderObj.__x_formattedName,
                "own": messages[i].__x_senderObj.__x_isMe
            }
            messages[i].__x_isNewMsg = false;
            temp.messages.push({
                message: messages[i].__x_body,
                timestamp: messages[i].__x_t,
                sender: sender
            });
        }
    }
    if(temp.messages.length > 0) {
        Output.push(temp);
    }
}
console.log("Unread messages: ", Output);
return Output;