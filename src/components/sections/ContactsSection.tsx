import Icon from "@/components/ui/icon";

const ContactsSection = () => {
  return (
    <>
      <section className="py-20 px-4 bg-accent text-black">
        <div className="container mx-auto">
          <div className="grid md:grid-cols-3 gap-12 text-center">
            <div>
              <div className="text-5xl font-light text-black mb-4">100%</div>
              <p className="text-lg">Качество услуг</p>
            </div>
            <div>
              <div className="text-5xl font-light text-black mb-4">2000+</div>
              <p className="text-lg">Довольных клиентов</p>
            </div>
            <div>
              <div className="text-5xl font-light text-black mb-4">20+</div>
              <p className="text-lg">Видов услуг</p>
            </div>
          </div>
        </div>
      </section>

      <section id="контакты" className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <p className="text-accent text-sm tracking-widest mb-4">КОНТАКТЫ</p>
            <h2 className="text-5xl font-light">Где нас найти</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-12 max-w-5xl mx-auto">
            <div className="space-y-8">
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <Icon name="MapPin" size={24} className="text-accent" />
                </div>
                <div>
                  <h3 className="text-xl font-light mb-2">Адрес</h3>
                  <p className="text-muted-foreground">Санкт-Петербург<br />ул. Авиаконструкторов, 8Б</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <Icon name="Phone" size={24} className="text-accent" />
                </div>
                <div>
                  <h3 className="text-xl font-light mb-2">Телефон</h3>
                  <p className="text-muted-foreground">
                    <a href="tel:+79992221192" className="hover:text-accent transition-colors">+7 (999) 222-11-92</a>
                    <br />
                    <a href="tel:+79322555126" className="hover:text-accent transition-colors">+7 (932) 255-51-26</a>
                  </p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="w-12 h-12 bg-accent/10 rounded-full flex items-center justify-center flex-shrink-0">
                  <Icon name="Clock" size={24} className="text-accent" />
                </div>
                <div>
                  <h3 className="text-xl font-light mb-2">Режим работы</h3>
                  <p className="text-muted-foreground">Ежедневно с 8:00 до 22:00</p>
                </div>
              </div>
            </div>
            <div className="h-[400px] bg-gray-200 rounded-lg overflow-hidden">
              <iframe
                src="https://yandex.ru/map-widget/v1/?ll=30.242916%2C60.011837&z=17&l=map&pt=30.242916,60.011837,pm2rdm"
                width="100%"
                height="100%"
                frameBorder="0"
                className="grayscale"
              ></iframe>
            </div>
          </div>
        </div>
      </section>
    </>
  );
};

export default ContactsSection;