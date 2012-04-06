using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;

namespace WindowsGame1
{
    class Elastic
    {
        public Vector2 Origin;

        public Vector2 Position;
        public Vector2 Speed;
        public Vector2 K;
        public float Friction;

        public Elastic()
        {

        }

        public void Update(GameTime gameTime)
        {
            float time = ((float)gameTime.ElapsedGameTime.Milliseconds) / 1000;

            Speed = Speed + ((Origin - Position) * K - Speed * Friction) * time;

            Position += Speed * time;
        }

    }
}
