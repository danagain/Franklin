const nodemailer = require('nodemailer');

const email = (body) => {

    const transporter = nodemailer.createTransport({
        service: 'gmail',
        auth: {
               user: 'thehunterofcoins@gmail.com',
               pass: process.env.EMAIL_PASS
           }
       }
    );

    // Message object
    const mailOptions = {
        from: 'thehunterofcoins@gmail.com', 
        to: process.env.EMAIL_TARGET,
        subject: `${body.BuyOrSell} - ${body.MarketName} - Hunted`, 
        html: `The ${body.BuyOrSell} for ${body.MarketName} at ${body.Quantity} was a ${body.success}`
      };

    transporter.sendMail(mailOptions, (error, info) => {
        if (error) {
            console.log('Error occurred');
            console.log(error.message);
        }
    });

}

module.exports = {
    email
}

