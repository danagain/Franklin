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
        subject: `${body.result.BuyOrSell} - ${body.result.MarketName} - Hunted`,
        html: `A ${body.result.BuyOrSell} for ${body.result.MarketName} - ${body.result.Quantity} shares at ${body.result.Rate} was purchased.`
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
