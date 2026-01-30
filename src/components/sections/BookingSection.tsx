const BookingSection = () => {
  return (
    <section id="запись" className="py-20 px-4 bg-black">
      <div className="container mx-auto max-w-2xl">
        <div className="text-center mb-12">
          <p className="text-accent text-sm tracking-widest mb-4">ОНЛАЙН ЗАПИСЬ</p>
          <h2 className="text-5xl font-light mb-4 text-white">Записаться на прием</h2>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-6">
            <a 
              href="https://mst.link/vasileva_viktoriya52" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all font-medium border border-white/20"
            >
              <span className="text-xl">💅</span>
              Виктория
            </a>
            <a 
              href="https://mst.link/popova_alena18" 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all font-medium border border-white/20"
            >
              <span className="text-xl">💅</span>
              Алена
            </a>
          </div>

          <p className="text-white mb-6">Запишитесь онлайн через Telegram бот — выбирайте мастера, услугу и удобное время</p>
          <a 
            href="https://t.me/promisslab_bot" 
            target="_blank" 
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 px-8 py-4 bg-accent text-black rounded-lg hover:bg-accent/90 transition-all font-bold text-lg shadow-lg"
          >
            <svg className="w-7 h-7" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.295-.6.295-.002 0-.003 0-.005 0l.213-3.054 5.56-5.022c.24-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.64-.203-.658-.64.135-.954l11.566-4.458c.538-.196 1.006.128.832.941z"/>
            </svg>
            Записаться через Telegram бот
          </a>
          <p className="text-white/70 text-base mt-6">📱 В боте: выбор мастера, свободных слотов времени и уведомления о записи</p>
        </div>

        <div className="bg-gradient-to-br from-accent/10 to-accent/5 backdrop-blur-sm rounded-2xl p-10 border border-accent/20">
          <div className="max-w-md mx-auto space-y-8">
            <div className="text-center">
              <div className="text-7xl mb-6">💬</div>
              <h3 className="text-3xl font-bold text-white mb-4">Удобная запись в боте</h3>
              <p className="text-white/60">Все возможности записи в одном месте</p>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-start gap-4 bg-black/30 p-4 rounded-lg">
                <span className="text-accent text-2xl mt-1">✓</span>
                <div>
                  <p className="text-white font-medium">Свободные слоты</p>
                  <p className="text-white/60 text-sm">Видите реальное время записи</p>
                </div>
              </div>
              
              <div className="flex items-start gap-4 bg-black/30 p-4 rounded-lg">
                <span className="text-accent text-2xl mt-1">✓</span>
                <div>
                  <p className="text-white font-medium">Выбор мастера</p>
                  <p className="text-white/60 text-sm">Записывайтесь к любимому специалисту</p>
                </div>
              </div>
              
              <div className="flex items-start gap-4 bg-black/30 p-4 rounded-lg">
                <span className="text-accent text-2xl mt-1">✓</span>
                <div>
                  <p className="text-white font-medium">Напоминания</p>
                  <p className="text-white/60 text-sm">Не пропустите свою запись</p>
                </div>
              </div>
              
              <div className="flex items-start gap-4 bg-black/30 p-4 rounded-lg">
                <span className="text-accent text-2xl mt-1">✓</span>
                <div>
                  <p className="text-white font-medium">Управление записями</p>
                  <p className="text-white/60 text-sm">Отменяйте и переносите в пару кликов</p>
                </div>
              </div>
            </div>
            
            <div className="text-center pt-4">
              <a 
                href="https://t.me/promisslab_bot" 
                target="_blank" 
                rel="noopener noreferrer"
                className="inline-flex items-center gap-3 px-8 py-4 bg-accent text-black rounded-lg hover:bg-accent/90 transition-all font-bold text-lg shadow-lg"
              >
                <svg className="w-7 h-7" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.894 8.221l-1.97 9.28c-.145.658-.537.818-1.084.508l-3-2.21-1.446 1.394c-.14.18-.357.295-.6.295-.002 0-.003 0-.005 0l.213-3.054 5.56-5.022c.24-.213-.054-.334-.373-.121l-6.869 4.326-2.96-.924c-.64-.203-.658-.64.135-.954l11.566-4.458c.538-.196 1.006.128.832.941z"/>
                </svg>
                Открыть бот для записи
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default BookingSection;