import puppeteer from 'puppeteer';

(async () => {
    console.log('PHASE 10: FRONTEND AUTOMATED TEST');
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    try {
        await page.goto('http://localhost:5175', { waitUntil: 'networkidle0' });
        console.log('Page loaded successfully.');
        
        const title = await page.title();
        console.log('Title:', title);
        
        const airportInput = await page.$('input#airport');
        const queryInput = await page.$('input#query');
        const investigateBtn = await page.$('.investigate-button');
        
        if (airportInput && queryInput && investigateBtn) {
            console.log('Form elements exist.');
        } else {
            console.error('Missing form elements!');
        }

        console.log('\nPHASE 11: FRONTEND VALIDATION');
        await airportInput.type('JFK');
        await investigateBtn.click();
        await page.waitForSelector('.error-message');
        const errorText = await page.$eval('.error-message', el => el.textContent);
        console.log('JFK Error:', errorText);
        
        await airportInput.click({ clickCount: 3 });
        await airportInput.press('Backspace');

        await airportInput.type('1234');
        await investigateBtn.click();
        await page.waitForSelector('.error-message');
        const errorText2 = await page.$eval('.error-message', el => el.textContent);
        console.log('1234 Error:', errorText2);

        await airportInput.click({ clickCount: 3 });
        await airportInput.press('Backspace');
        
        await queryInput.click({ clickCount: 3 });
        await queryInput.press('Backspace');
        await airportInput.type('KJFK');
        await investigateBtn.click();
        await page.waitForSelector('.error-message');
        const errorText3 = await page.$eval('.error-message', el => el.textContent);
        console.log('Empty Query Error:', errorText3);

        console.log('\nSubmitting KJFK...');
        await queryInput.type('Investigate current operational conditions.');
        await investigateBtn.click();
        
        const loading = await page.$('.loading-spinner');
        if (loading) console.log('Loading state appeared.');
        
        await page.waitForSelector('.results-section', { timeout: 120000 });
        console.log('Results rendered successfully.');
        
        const returnedAirport = await page.$eval('.airport-heading h3', el => el.textContent);
        console.log('Displayed Airport:', returnedAirport);
        
        const verifiedBadge = await page.$('.verification-badge');
        if (verifiedBadge) console.log('Verification badge visible.');

        console.log('\nPHASE 12: FRONTEND MULTI-AIRPORT TEST');
        console.log('Testing KLAX...');
        await airportInput.click({ clickCount: 3 });
        await airportInput.press('Backspace');
        await airportInput.type('KLAX');
        await investigateBtn.click();
        await page.waitForSelector('.loading-spinner');
        await page.waitForSelector('.results-section', { timeout: 120000 });
        const klaxAirport = await page.$eval('.airport-heading h3', el => el.textContent);
        console.log('Displayed Airport:', klaxAirport);
        
    } catch (e) {
        console.error(e);
    } finally {
        await browser.close();
    }
})();
