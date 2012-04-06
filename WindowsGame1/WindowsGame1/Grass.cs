using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using Microsoft.Xna.Framework;

namespace WindowsGame1
{
    class Grass
    {
        private Elastic _angles;
        private Vector2 _position;
        private Vector2 _length;

        public Grass(Vector2 position, Vector2 length, Vector2 k, float friction = 0.95f)
        {
            _position = position;
            _length = length;
            _angles = new Elastic()
                          {
                              Origin = new Vector2((float)(Math.PI / 2), (float)(Math.PI / 2)),
                              Friction = friction,
                              Position = new Vector2((float)(Math.PI / 2 - 0.02f), (float)(Math.PI / 2 + 0.04f)),
                              Speed = new Vector2(),
                              K = k
                          };
        }

        public void Draw(SpriteBatchEx spriteBatch, GameTime time)
        {
            _angles.Update(time);

            Vector2 pos2;
            pos2.X = _position.X + (float) Math.Cos(_angles.Position.X)*_length.X;
            pos2.Y = _position.Y + (float) Math.Sin(_angles.Position.X)*_length.X;

            spriteBatch.DrawLine(_position, pos2, Color.Green, 3);


            Vector2 pos3;
            pos3.X = pos2.X + (float)Math.Cos(_angles.Position.X + _angles.Position.Y) * _length.Y;
            pos3.Y = pos2.Y + (float)Math.Sin(_angles.Position.X + _angles.Position.Y) * _length.Y;

            spriteBatch.DrawLine(pos2, pos3, Color.Green, 2);

        }
    }
}
