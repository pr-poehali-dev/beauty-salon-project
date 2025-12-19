import { Card, CardContent } from "@/components/ui/card";
import Icon from "@/components/ui/icon";

interface ServicesSectionProps {
  scrollToSection: (id: string) => void;
}

const ServicesSection = ({ scrollToSection }: ServicesSectionProps) => {
  const services = [
    {
      category: "Маникюр",
      items: [
        { name: "Аппаратный маникюр", price: "500 ₽" },
        { name: "Выравнивание ногтевой пластины", price: "500 ₽" },
        { name: "Покрытие с градиентом (омбре)", price: "1000 ₽" },
        { name: "Детский маникюр", price: "500 ₽" },
        { name: "Дизайн ногтей", price: "500 ₽" }
      ]
    },
    {
      category: "Наращивание и коррекция",
      items: [
        { name: "Коррекция наращённых ногтей", price: "1800 ₽" },
        { name: "Мужской маникюр", price: "1000 ₽" },
        { name: "Маникюр с покрытием гель-лаком", price: "1000 ₽" },
        { name: "Наращивание ногтей", price: "1900 ₽" }
      ]
    },
    {
      category: "Покрытие ногтей",
      items: [
        { name: "Покрытие ногтей на руках гель-лаком", price: "500 ₽" },
        { name: "Покрытие ногтей на руках биогелем", price: "500 ₽" },
        { name: "Ремонт ногтя", price: "180 ₽" }
      ]
    },
    {
      category: "Снятие покрытия",
      items: [
        { name: "Снятие биогеля", price: "500 ₽" },
        { name: "Снятие гель-лака с ногтей на руках", price: "500 ₽" },
        { name: "Снятие наращённых ногтей", price: "1000 ₽" }
      ]
    },
    {
      category: "Специальные процедуры",
      items: [
        { name: "Укрепление ногтей", price: "800 ₽" },
        { name: "Японский маникюр", price: "800 ₽" }
      ]
    }
  ];

  return (
    <>
      <section id="услуги" className="py-20 px-4 bg-secondary/30">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <p className="text-accent text-sm tracking-widest mb-4">НАШИ УСЛУГИ</p>
            <h2 className="text-5xl font-light">Спектр возможностей</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: "Sparkles", title: "Ногтевой сервис", desc: "Маникюр, педикюр, наращивание" },
              { icon: "Waves", title: "Массаж и коррекция", desc: "LPG, лимфодренаж, прессотерапия" },
              { icon: "Heart", title: "Уход за лицом", desc: "Чистка, биоревитализация, уходы" },
              { icon: "Scissors", title: "Депиляция", desc: "Все виды эпиляции" },
              { icon: "Brush", title: "Перманентный макияж", desc: "Татуаж бровей, губ, век" },
              { icon: "Eye", title: "Брови и ресницы", desc: "Ламинирование, окрашивание, наращивание" }
            ].map((service, idx) => (
              <Card 
                key={idx} 
                className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300 group cursor-pointer"
                onClick={() => scrollToSection("прайс")}
              >
                <CardContent className="p-8 text-center">
                  <div className="w-16 h-16 mx-auto mb-6 bg-accent/10 rounded-full flex items-center justify-center group-hover:bg-accent/20 transition-colors">
                    <Icon name={service.icon} size={28} className="text-accent" />
                  </div>
                  <h3 className="text-2xl font-light mb-3">{service.title}</h3>
                  <p className="text-muted-foreground">{service.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section id="прайс" className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center mb-16">
            <p className="text-accent text-sm tracking-widest mb-4">ПРАЙС-ЛИСТ</p>
            <h2 className="text-5xl font-light">Стоимость услуг</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
            {services.map((category, idx) => (
              <Card key={idx} className="border border-gray-200 shadow-md">
                <CardContent className="p-8">
                  <h3 className="text-2xl font-light mb-6 pb-4 border-b border-accent/30">
                    {category.category}
                  </h3>
                  <div className="space-y-4">
                    {category.items.map((item, itemIdx) => (
                      <div key={itemIdx} className="flex justify-between items-start gap-4">
                        <span className="text-foreground">{item.name}</span>
                        <span className="text-accent font-medium whitespace-nowrap">{item.price}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>
    </>
  );
};

export default ServicesSection;
